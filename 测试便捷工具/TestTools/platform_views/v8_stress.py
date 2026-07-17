import streamlit as st
import time
import json
import re
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
from curlparser import parse as parse_curl


def render_stress_view():
    st.subheader("⚡ 接口高性能并发压测机 (cURL Stress Tester)")
    st.caption("直接粘贴抓包获得的标准 cURL 命令行，指定并发线程与执行轮次，秒级获取专业的耗时白皮书与统计报告。")

    # 1. 动态版本 Key 销毁机制（解决清空面板卡死）
    if "stress_editor_version" not in st.session_state:
        st.session_state["stress_editor_version"] = 0

    st.markdown("##### 💻 1. 请输入/粘贴标准的 cURL 命令")
    from streamlit_ace import st_ace

    # 使用大容量的 Ace 编辑器提升用户粘贴 curl 的体验
    editor_key = f"curl_ace_editor_v_{st.session_state['stress_editor_version']}"
    curl_input_raw = st_ace(
        value="",
        language="sh",
        theme="monokai",
        key=editor_key,
        height=260,
        font_size=13,
        show_gutter=True,
        wrap=True,
        auto_update=True
    )

    # 2. 压测核心控制面板
    st.markdown("##### ⚙️ 2. 压测策略配置 center")
    col_cfg1, col_cfg2, col_cfg3 = st.columns(3)  # 👈 扩展为 3 列
    with col_cfg1:
        total_runs = st.number_input("🔄 总调用次数 (Total Requests):", min_value=1, max_value=2000, value=10, step=10,
                                     key="stress_total_runs")
    with col_cfg2:
        max_workers = st.number_input("🧵 并发线程数 (Max Concurrent Threads):", min_value=1, max_value=100, value=2,
                                      step=1, key="stress_max_workers")
    with col_cfg3:
        # 🟢 【新增控速组件】：支持浮点数（如 0.1 秒、0.5 秒），默认 0.0 表示全速冲刷不限速
        delay_seconds = st.number_input("⏳ 请求间隔秒数 (Delay Seconds):", min_value=0.0, max_value=60.0, value=0.0,
                                        step=0.1, format="%.2f", key="stress_delay_seconds")

    # ==========================================
    # # 3. 交互控制按钮
    # ==========================================
    col_btn1, col_btn2 = st.columns([8, 2])
    with col_btn1:
        submit_stress = st.button("🚀 提请全量并发压测 (Start Load Test)", type="primary", key="btn_run_stress",
                                  use_container_width=True)
    with col_btn2:
        clear_stress = st.button("🗑️ 清空面板", key="btn_clear_stress", use_container_width=True)

    # 🛑 联动修改点：完善清空面板的底层逻辑
    if clear_stress:
        # 1. 物理斩断并清除历史报告与统计缓存
        st.session_state["cache_stress_test_report"] = None
        st.session_state["cache_stress_test_summary"] = None

        # 2. 强制将控速组件输入框的值重置回 0.00
        if "stress_delay_seconds" in st.session_state:
            st.session_state["stress_delay_seconds"] = 0.00

        # 3. 压测输入框的版本计数器累加（强刷 Ace 编辑器绑定的 Key，从而清空粘贴的 curl）
        st.session_state["stress_editor_version"] += 1

        st.toast("压测面板、配置及历史报告已全部初始化清空！", icon="🧹")
        st.rerun()

    # ==========================================
    # 🚀 4. 压测核心引擎执行区
    # ==========================================
    if submit_stress:
        # 清理 Windows cmd 复制出来可能带的换行连接符 ^ 或 \
        clean_curl = curl_input_raw.replace('^\n', ' ').replace('\\\n', ' ').strip()
        clean_curl = re.sub(r'\s*\^\s*', ' ', clean_curl)
        clean_curl = re.sub(r'\s*\\\s*', ' ', clean_curl)

        if not clean_curl.startswith("curl"):
            st.error("❌ 语法错误：输入的文本看起来不是一个合法的 cURL 命令，请以 `curl` 开头！")
        else:
            with st.spinner("⚡ 压测引擎已全面点火，正在以指定的并发格栅进行请求冲刷..."):
                try:
                    # 🧬 【终极防御性解析】：用正则和原生逻辑完美提取 URL, Headers 和 Method
                    url_match = re.search(r"curl\s+.*?['\"]?(https?://[^\s'\"]+)['\"]?", clean_curl, re.IGNORECASE)
                    if not url_match:
                        url_match = re.search(r"(https?://[^\s'\"]+)", clean_curl)

                    if not url_match:
                        st.error("❌ 解析失败：未能从 cURL 命令中识别出合法的 请求 URL！")
                        return

                    req_url = url_match.group(1).strip()

                    # 🌐 🔥【核心修改点 1】：利用 urlparse 动态安全解析出接口的纯净 Path 路径
                    from urllib.parse import urlparse
                    parsed_url = urlparse(req_url)
                    req_path = parsed_url.path  # 例如：/api/member

                    req_method = "GET"
                    if re.search(r"-X\s+(POST|PUT|DELETE|PATCH)", clean_curl, re.IGNORECASE):
                        req_method = re.search(r"-X\s+(POST|PUT|DELETE|PATCH)", clean_curl, re.IGNORECASE).group(
                            1).upper()
                    elif "--data" in clean_curl or "-d " in clean_curl or "--json" in clean_curl:
                        req_method = "POST"

                    req_headers = {}
                    header_matches = re.findall(r"(?:-H|--header)\s+['\"]([^'\"]+)['\"]", clean_curl)
                    for h in header_matches:
                        if ":" in h:
                            k, v = h.split(":", 1)
                            req_headers[k.strip().replace("^", "")] = v.strip().replace("^", "")

                    req_data = None
                    req_json = None
                    data_match = re.search(r"(?:--data-raw|--data|-d)\s+['\"]([^'\"]+)['\"]", clean_curl)
                    if data_match:
                        raw_body = data_match.group(1).strip()
                        try:
                            req_json = json.loads(raw_body)
                        except:
                            req_data = raw_body

                except Exception as parse_err:
                    st.error(f"🛑 cURL 自研解析器发生未知异常！详情: `{str(parse_err)}`")
                    return

                # 定义单次请求原子任务
                def single_request_task(request_index):
                    if delay_seconds > 0:
                        time.sleep((request_index - 1) * delay_seconds)

                    start_time = time.perf_counter()
                    try:
                        res = requests.request(
                            method=req_method,
                            url=req_url,
                            headers=req_headers,
                            data=req_data,
                            json=req_json,
                            timeout=15
                        )
                        duration = (time.perf_counter() - start_time) * 1000
                        return {
                            "序号": request_index,
                            "请求Path": req_path,  # 👈 将解析出的 Path 动态打入每一行流水中
                            "HTTP状态码": res.status_code,
                            "耗时(ms)": round(duration, 2),
                            "执行状态": "🟢 成功",
                            "响应概要": res.text[:60] + "..." if res.text else "空响应"
                        }
                    except Exception as req_err:
                        duration = (time.perf_counter() - start_time) * 1000
                        return {
                            "序号": request_index,
                            "请求Path": req_path,  # 👈 失败请求同样记录对应的 Path
                            "HTTP状态码": 0,
                            "耗时(ms)": round(duration, 2),
                            "执行状态": "🔴 失败",
                            "响应概要": f"异常: {str(req_err)[:50]}"
                        }

                # 🚀 线程池并发池调度
                results_list = []
                progress_bar = st.progress(0.0)
                status_text = st.empty()

                with ThreadPoolExecutor(max_workers=int(max_workers)) as executor:
                    futures = {executor.submit(single_request_task, i + 1): i for i in range(int(total_runs))}
                    completed_count = 0
                    for future in as_completed(futures):
                        task_res = future.result()
                        results_list.append(task_res)
                        completed_count += 1
                        progress_percentage = completed_count / int(total_runs)
                        progress_bar.progress(progress_percentage)
                        status_text.caption(f"📊 已完成并发冲刷: `{completed_count} / {total_runs}` 轮轮次...")

                # 强行写入全局状态机，确保变量名与下方判定完全一致
                df = pd.DataFrame(results_list).sort_values(by="序号").reset_index(drop=True)
                st.session_state["cache_stress_test_report"] = df
                st.rerun()

    # ==========================================
    # 📥 5. 压测报告看板深度呈现与多维筛选（独立渲染区）
    # ==========================================
    if st.session_state.get("cache_stress_test_report") is not None:
        report_df = st.session_state["cache_stress_test_report"]

        st.markdown("---")
        st.markdown("### 📊 接口性能数据白皮书 (Summary Report)")

        # 🟢【终极防御性修复】：绕开 Pandas 的特殊列索引寻址，直接通过标准的 columns 列表和 to_dict() 安全提取
        current_path = "未知路径"
        if not report_df.empty and "请求Path" in report_df.columns:
            try:
                # 提取第一行并转化为字典，使用原生 .get() 绝对不会报 KeyError
                first_row = report_df.iloc[0].to_dict()
                current_path = first_row.get("请求Path", "未知路径")
            except Exception:
                current_path = "未知路径"

        # 挂载转换后的 Path 路径提示
        st.info(f"🛣️ **当前压测目标路径 (Target Path):** `{current_path}`")
        # 1. 过滤状态控制器
        st.markdown("##### 🔍 明细日志动态筛选 (Log Filter)")
        filter_status = st.radio(
            "过滤展示状态：",
            ["✨ 显示全部请求", "🟢 仅显示成功请求", "🔴 仅显示失败请求"],
            horizontal=True,
            key="stress_log_filter_status"
        )

        # 2. 实时对局部 DataFrame 进行切片
        if "仅显示成功请求" in filter_status:
            filtered_df = report_df[report_df["执行状态"] == "🟢 成功"]
            display_tip = f"🎯 已过滤：当前仅展示成功请求，共 `{len(filtered_df)}` 条记录。"
        elif "仅显示失败请求" in filter_status:
            filtered_df = report_df[report_df["执行状态"] == "🔴 失败"]
            display_tip = f"🚨 已过滤：当前仅展示失败请求，共 `{len(filtered_df)}` 条记录。"
        else:
            filtered_df = report_df
            display_tip = f"📄 当前展示全部流水日志，共 `{len(filtered_df)}` 条记录。"

        # 3. 实时基于 filtered_df 计算卡片实时动态指标
        if len(filtered_df) > 0:
            current_success_df = filtered_df[filtered_df["执行状态"] == "🟢 成功"]
            avg_time = filtered_df["耗时(ms)"].mean()
            max_time = filtered_df["耗时(ms)"].max()
            min_time = filtered_df["耗时(ms)"].min()
            success_rate = (len(current_success_df) / len(filtered_df)) * 100

            avg_str = f"{round(avg_time, 2)} ms"
            range_str = f"{round(max_time, 2)} / {round(min_time, 2)} ms"
            rate_str = f"{round(success_rate, 2)}%"
        else:
            avg_str = "0.00 ms"
            range_str = "0.00 / 0.00 ms"
            rate_str = "0.00%"

        # 4. 指标卡片高亮呈现
        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        with col_m1:
            st.metric("当前筛选平均耗时 (Avg)", avg_str)
        with col_m2:
            st.metric("最长 / 最短耗时", range_str)
        with col_m3:
            st.metric("当前数据成功率", rate_str,
                      delta=None if "成功" in filter_status or len(filtered_df) == 0 else "⚠️ 存在接口风险")
        with col_m4:
            st.metric("展示数 / 总请求数", f"{len(filtered_df)} / {len(report_df)} 次")

        st.markdown("---")

        # 5. 明细折叠看板渲染
        with st.expander("📄 查看接口请求耗时明细流水 (Filtered Table Logs)", expanded=True):
            if "失败" in filter_status and len(filtered_df) == 0:
                st.success("🎉 太棒了！本次压测没有产生任何失败请求。")
            elif "成功" in filter_status and len(filtered_df) == 0:
                st.error("💥 警报：本次压测没有任何请求成功，请检查网络或 cURL 凭证！")
            else:
                st.caption(display_tip)
                st.dataframe(filtered_df, use_container_width=True)