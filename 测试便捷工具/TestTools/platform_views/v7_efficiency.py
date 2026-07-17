import streamlit as st
import time
import pytz
from datetime import datetime
import json
import os
from database import run_db_query, init_db_connection


def render_efficiency_view():
    st.subheader("🛠️ 团队研发与测试效率工具箱 (局域网公共站)")
    tab_timestamp, tab_json, tab_qrcode, tab_database, tab_world_time = st.tabs([
        "⏰ 时间戳双向转换", "📄 JSON 格式化与解析", "🔗 链接/文本转二维码", "🔍 数据库工作台", "🌐 世界时钟看板"
    ])

    is_prod = st.session_state.is_prod

    timezone_dict = {
        "北京/中国标准时间 (Asia/Shanghai)": "Asia/Shanghai", "新加坡/东南亚 (Asia/Singapore)": "Asia/Singapore",
        "伦敦/英国标准时间 (Europe/London)": "Europe/London",
        "洛杉矶/太平洋时间 (America/Los_Angeles)": "America/Los_Angeles",
        "纽约/美东时间 (America/New_York)": "America/New_York", "UTC 世界协调时间 (UTC)": "UTC"
    }

    with tab_timestamp:
        st.markdown("### 🕒 时间戳正反向便捷转换面板")
        current_ts_val = int(time.time())
        st.markdown(
            f"<h1 style='color: #1c7ed6; font-family: monospace; margin-top: 5px; margin-bottom: 5px; font-size: 42px;'>{current_ts_val} <span style='font-size: 18px; color: #868e96; font-weight: normal;'>秒 (最新静态截取)</span></h1>",
            unsafe_allow_html=True)
        if st.button("🔄 手动捕捉最新时间戳"): st.rerun()

        st.markdown("---")
        st.markdown("#### 🕒 时间戳转日期时间")
        col_t1, col_t2, col_t3, col_t4 = st.columns([3, 2, 1.2, 3.8])
        with col_t1:
            if "user_manual_ts_input" not in st.session_state: st.session_state["user_manual_ts_input"] = str(
                current_ts_val)
            input_ts_str = st.text_input("请输入时间戳 (10位秒级):", value=st.session_state["user_manual_ts_input"],
                                         key="ts_to_date_input_val")
            if input_ts_str != st.session_state["user_manual_ts_input"]: st.session_state[
                "user_manual_ts_input"] = input_ts_str
        with col_t2:
            ts_unit = st.selectbox("单位:", ["秒(s)", "毫秒(ms)"], key="ts_to_date_unit_select")
        with col_t3:
            st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
            convert_ts_click = st.button("⚡ 转换", key="btn_action_ts_to_date")
        with col_t4:
            selected_tz_label_1 = st.selectbox("目标时区 (Timezone):", list(timezone_dict.keys()), index=2,
                                               key="ts_to_date_tz_select")
            target_tz_1 = timezone_dict[selected_tz_label_1]

        if convert_ts_click and input_ts_str.strip():
            try:
                cleaned_ts = float(input_ts_str.strip())
                if "毫秒" in ts_unit: cleaned_ts = cleaned_ts / 1000.0
                st.session_state["cache_ts_to_date_res"] = datetime.fromtimestamp(cleaned_ts, pytz.utc).astimezone(
                    pytz.timezone(target_tz_1)).strftime("%Y-%m-%d %H:%M:%S")
            except Exception:
                st.session_state["cache_ts_to_date_res"] = "❌ 格式非法"
        st.text_input("📅 转换出的日期时间结果:", value=st.session_state.cache_ts_to_date_res, disabled=True)

        st.markdown("<div style='margin-top: 25px;'></div>", unsafe_allow_html=True)
        st.markdown("#### 📅 日期时间转时间戳")
        col_d1, col_d2, col_d3, col_d4 = st.columns([3, 2, 1.2, 3.8])
        with col_d1:
            if "user_manual_date_input" not in st.session_state: st.session_state[
                "user_manual_date_input"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            input_date_str = st.text_input("请输入日期时间 (格式必须对齐):",
                                           value=st.session_state["user_manual_date_input"], key="date_to_ts_input_val")
            if input_date_str != st.session_state["user_manual_date_input"]: st.session_state[
                "user_manual_date_input"] = input_date_str
        with col_d2:
            selected_tz_label_2 = st.selectbox("输入源时区 (Timezone):", list(timezone_dict.keys()), index=3,
                                               key="date_to_ts_tz_select")
            target_tz_2 = timezone_dict[selected_tz_label_2]
        with col_d3:
            st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
            convert_date_click = st.button("⚡ 转换", key="btn_action_date_to_ts")
        with col_d4:
            date_to_ts_unit = st.selectbox("期望输出单位:", ["秒(s)", "毫秒(ms)"], key="date_to_ts_unit_select")

        if convert_date_click and input_date_str.strip():
            try:
                naive_dt = datetime.strptime(input_date_str.strip(), "%Y-%m-%d %H:%M:%S")
                local_dt = pytz.timezone(target_tz_2).localize(naive_dt)
                final_timestamp = local_dt.timestamp()
                st.session_state["cache_date_to_ts_res"] = str(
                    int(final_timestamp * 1000 if "毫秒" in date_to_ts_unit else final_timestamp))
            except Exception:
                st.session_state["cache_date_to_ts_res"] = "❌ 格式解析失败"
        st.text_input("🔢 转换出的时间戳结果:", value=st.session_state.cache_date_to_ts_res, disabled=True)

    with tab_json:
        st.markdown("### 📄 结构化 JSON 数据高亮排版器")
        with st.form("json_parser_form"):
            json_input_raw = st.text_area("请粘贴需要解析的原始 JSON 文本：",
                                          value=st.session_state.get("tab7_json_input", ""), height=250,
                                          key="tab7_json_input")
            col_js_l, col_js_r = st.columns([8, 2])
            with col_js_l: submit_json = st.form_submit_button("⚡ 立即执行格式化排版", type="primary")
            with col_js_r: clear_json = st.form_submit_button("🧹 清除结果树")
        if clear_json: st.session_state["tab7_json_output_cache"] = None; st.rerun()
        if submit_json:
            if not json_input_raw.strip():
                st.error("❌ 无法解析：输入框内容为空！")
            else:
                try:
                    st.session_state["tab7_json_output_cache"] = {"status": "success",
                                                                  "data": json.loads(json_input_raw.strip())}
                except json.JSONDecodeError as je:
                    st.session_state["tab7_json_output_cache"] = {"status": "error", "msg": str(je)}
        if st.session_state["tab7_json_output_cache"] is not None:
            json_cache = st.session_state["tab7_json_output_cache"]
            st.markdown("---")
            if json_cache["status"] == "success":
                st.success("🎉 JSON 语法校验通过！"); st.json(json_cache["data"])
            else:
                st.error(f"❌ 解析失败: {json_cache['msg']}")

    with tab_qrcode:
        st.markdown("### 🔗 移动端联调：多功能二维码生成中心")
        col_qr_l, col_qr_r = st.columns([2, 1])
        with col_qr_l:
            qr_text_raw = st.text_area("请输入需要转换的 URL 链接或文本内容：",
                                       value="https://gray-reward.reelshort.com/?uid=913909995", height=120,
                                       key="tab7_qr_input")
            generate_qr_trigger = st.button("🚀 立即生成高清二维码", type="primary", key="btn_qrcode_action")
        with col_qr_r:
            if "tab7_cached_qr_bytes" not in st.session_state: st.session_state["tab7_cached_qr_bytes"] = None
            if generate_qr_trigger or (st.session_state["tab7_cached_qr_bytes"] is not None):
                import qrcode
                from io import BytesIO
                if generate_qr_trigger and qr_text_raw.strip():
                    qr = qrcode.QRCode(version=3, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10,
                                       border=4)
                    qr.add_data(qr_text_raw.strip())
                    qr.make(fit=True)
                    buf = BytesIO()
                    qr.make_image().save(buf, format="PNG")
                    st.session_state["tab7_cached_qr_bytes"] = buf.getvalue()
                if st.session_state["tab7_cached_qr_bytes"]: st.image(st.session_state["tab7_cached_qr_bytes"],
                                                                      width=220)

    with tab_database:
        st.markdown("### 🔍 平台高阶数据沙盒 (DB Workbench)")
        st.caption("支持实时联调测试库，查询用户流水的底层落库状态。")
        # 🔥【修复核心点 1】：初始化一个组件版本计数器，如果内存里没有则设为 0
        if "sql_editor_version" not in st.session_state:
            st.session_state["sql_editor_version"] = 0

        # 1. 自动长连接活性探测
        if st.session_state["db_connection_handle"] is None and st.session_state["db_connect_error"] is None:
            with st.spinner("正在首次建立与阿里云 RDS 的数据库连接..."):
                st.session_state["db_connection_handle"] = init_db_connection()
        is_db_alive = False
        if st.session_state["db_connection_handle"] is not None:
            try:
                st.session_state["db_connection_handle"].ping(reconnect=True); is_db_alive = True
            except Exception as ping_err:
                st.session_state["db_connect_error"] = str(ping_err);
                st.cache_resource.clear();
                st.session_state["db_connection_handle"] = None
        if not is_db_alive:
            st.error("🚨 当前平台与阿里云 RDS 数据库连接已断开（或初始化失败）。")
            if st.session_state.get("db_connect_error"):
                st.markdown("**🛑 底层原始错误回执：**")
                st.code(st.session_state["db_connect_error"], language="python")
            col_recon1, col_recon2 = st.columns([7, 3])
            with col_recon1:
                st.info(
                    "💡 排查指引：请根据上方回执进行排查。如果是 `timed out`，请 100% 优先去阿里云 RDS 后台看白名单是否放行了你当前的公网 IP。")
            with col_recon2:
                if st.button("⚡ 立即发起断线重连", type="primary", key="btn_force_reconnect_db",
                             use_container_width=True):
                    with st.spinner("正在重新握手测试库网关..."):
                        st.cache_resource.clear()
                        st.session_state["db_connection_handle"] = init_db_connection()
                        if st.session_state["db_connection_handle"] is not None:
                            st.toast("🎉 数据库长连接重建成功！", icon="🔌"); st.success("✅ 重连成功！"); st.rerun()
                        else:
                            st.error("❌ 重连依然失败。"); st.rerun()
            st.markdown("---")
        else:
            st.caption("🟢 平台底层数据库长连接：**已在线 (Connected)**")

            # ==========================================
            # 📁 🔥【强力重构区】：防御式 SQL 文件热加载引擎
            # ==========================================
            # ==========================================
            # 📁 🔥【强力重构区】：防御式 SQL 文件热加载引擎
            # ==========================================
            def load_default_sql(file_path):
                fallback = "-- 请在下方输入SQL语句\nSELECT * FROM user_member_tab LIMIT 5;"
                if not file_path:
                    return fallback

                # 规避 Windows 绝对路径符号截断，强行标准化路径
                normalized_path = os.path.normpath(file_path.strip())

                if not os.path.exists(normalized_path):
                    st.error(f"❌ 物理文件未找到！请检查路径是否存在：`{normalized_path}`")
                    return fallback

                # 采用多编码自适应探测读取，防止因文件的 UTF-8 / GBK 编码冲突导致读取流静默崩溃
                for encoding_type in ["utf-8", "gbk", "utf-8-sig"]:
                    try:
                        with open(normalized_path, "r", encoding=encoding_type) as f:
                            content = f.read().strip()
                            if content:
                                return content
                    except Exception as read_err:
                        # 如果读取失败，继续尝试下一种编码
                        continue

                # 如果走到这里说明所有编码都失败了，抛出具体的系统错误协助 debug
                try:
                    with open(normalized_path, "r", encoding="utf-8") as f:
                        f.read()
                except Exception as final_err:
                    st.error(f"🛑 读盘发生核心权限或损坏故障: `{str(final_err)}`")

                return fallback

            # 锁定你的本地物理 SQL 路径（使用 r'' 原始字符串彻底杜绝 \n \t 反斜杠转义恶性 Bug）
            sql_template_file = r"E:\桌面\工程\测试便捷工具\TestTools\prod_default.sql"

            # 页面级交互控制台
            col_file_l, col_file_r = st.columns([8, 2])
            with col_file_r:
                if st.button("📂 强制从本地重载 SQL 文件", key="btn_force_reload_sql_io", use_container_width=True):
                    # 1. 强行将文本池洗为空字符串，放行下一次重绘时顶部的 load_default_sql() 读盘逻辑
                    st.session_state["custom_sql_input"] = ""
                    st.session_state["cache_db_query_res"] = None

                    # 2. 🔥【核心修复点】：重载文件时，也让版本号自增 1！
                    # 这样页面重绘时，Ace 组件的 Key 会变掉，前端缓存被强行物理销毁，新读取的 SQL 就能秒级灌进去了
                    st.session_state["sql_editor_version"] += 1

                    st.toast("已成功绕过缓存，强制从磁盘重载最新SQL！", icon="💾")
                    st.rerun()

            # 状态机防空锁：如果当前内存是空的、不存在、或者处于清空状态，强制去读盘
            if (
                    "custom_sql_input" not in st.session_state
                    or st.session_state["custom_sql_input"] in ["", "-- 已清空，请输入SQL\n"]
            ):  # 🟢 🔥【核心修复点 2】
                st.session_state["custom_sql_input"] = load_default_sql(sql_template_file)

            st.markdown("---")
            from streamlit_ace import st_ace
            st.markdown("##### 💻 SQL 编辑器")

            # 核心交互 Ace 编辑器组件
            # 🔥【修复核心点 2】：将 key 动态化绑定，强制刷新前端缓存
            editor_key = f"sql_ace_editor_v_{st.session_state['sql_editor_version']}"

            sql_input = st_ace(
                value=st.session_state["custom_sql_input"],
                language="sql",
                theme="monokai",
                key=editor_key,  # 🟢 动态绑定版本 Key
                height=600,
                font_size=14,
                tab_size=4,
                show_gutter=True,
                show_print_margin=False,
                wrap=True,
                auto_update=True  # 保持实时同步
            )

            # 实时将编辑器的最新输入写回全局状态机，防止切换菜单时数据丢失
            st.session_state["custom_sql_input"] = sql_input

        col_db_btn1, col_db_btn2 = st.columns([8, 2])
        with col_db_btn1:
            submit_query = st.button("⚡ 提请数据查询 (Run Query)", type="primary", key="btn_run_sql")
        with col_db_btn2:
            clear_query = st.button("🗑️ 清空面板", key="btn_clear_sql")

        # 🔥【终极修复点】：移除对组件私有 Key 的显式修改，只做版本迭代
        if clear_query:
            # 1. 只修改我们自己定义的文本状态机，这个是可以任意改写的
            st.session_state["custom_sql_input"] = "-- 已清空，请输入SQL语句\n"
            st.session_state["cache_db_query_res"] = None

            # 2. 核心大招：让版本号自增 1。
            # 下一行执行时，组件 Key 会变成 v_1，旧的 v_0 以及它的顽固缓存会被 Streamlit 自动全量回收，绝不报错！
            st.session_state["sql_editor_version"] += 1
            st.rerun()

        if submit_query:
            clean_sql = "\n".join([line for line in sql_input.split("\n") if not line.strip().startswith("--")])
            if not clean_sql.strip():
                st.error("❌ SQL 语句不能为空！")
            elif not clean_sql.strip().lower().startswith("select"):
                st.warning("⚠️ 灰度安全控制：本工作台仅支持高危放行的 `SELECT` 只读查询指令！")
            else:
                with st.spinner("正在安全透传测试库网关..."):
                    st.session_state["cache_db_query_res"] = run_db_query(clean_sql.strip())
        if st.session_state["cache_db_query_res"] is not None:
            db_data = st.session_state["cache_db_query_res"]
            st.markdown("#### 📥 结构化查询回执")
            if not db_data:
                st.info("💡 查询执行成功，但未检索到符合条件的记录（Result Empty）。")
            else:
                st.success(f"🎉 成功击中 `{len(db_data)}` 条数据！")
                import pandas as pd
                st.dataframe(pd.DataFrame(db_data), use_container_width=True)

    with tab_world_time:
        st.markdown("### 🌐 全球测试业务核心时区监控大盘")
        st.caption("实时对齐美洲、欧洲、亚洲、非洲等核心互动剧出海业务落库的物理服务器时区状态。")
        regions_data = {
            "🌎 美洲节点": [
                {"name": "加拿大 · 温哥华", "tz": "America/Vancouver", "flag": "🇨🇦"},
                {"name": "加拿大 · 多伦多", "tz": "America/Toronto", "flag": "🇨🇦"},
                {"name": "美国 · 洛杉矶", "tz": "America/Los_Angeles", "flag": "🇺🇸"},
                {"name": "美国 · 凤凰城", "tz": "America/Phoenix", "flag": "🇺🇸"},
                {"name": "美国 · 丹佛", "tz": "America/Denver", "flag": "🇺🇸"},
                {"name": "美国 · 芝加哥", "tz": "America/Chicago", "flag": "🇺🇸"},
                {"name": "美国 · 纽约", "tz": "America/New_York", "flag": "🇺🇸"},
                {"name": "墨西哥 · 墨西哥城", "tz": "America/Mexico_City", "flag": "🇲🇽"},
                {"name": "哥伦比亚 · 波哥大", "tz": "America/Bogota", "flag": "🇨🇴"},
                {"name": "秘鲁 · 利马", "tz": "America/Lima", "flag": "🇵🇪"},
                {"name": "巴西 · 圣保罗", "tz": "America/Sao_Paulo", "flag": "🇧🇷"},
                {"name": "阿根廷 · 布宜诺斯艾利斯", "tz": "America/Argentina/Buenos_Aires", "flag": "🇦🇷"},
                {"name": "智利 · 圣地扬哥", "tz": "America/Santiago", "flag": "🇨🇱"}
            ],
            "🌊 太平洋节点": [
                {"name": "美国 · 檀香山", "tz": "Pacific/Honolulu", "flag": "🇺🇸"},
                {"name": "澳大利亚 · 悉尼", "tz": "Australia/Sydney", "flag": "🇦🇺"},
                {"name": "新西兰 · 奥克兰", "tz": "Pacific/Auckland", "flag": "🇳🇿"}
            ],
            "🇪🇺 西欧时间 (WET) / 中欧时间 (CET)": [
                {"name": "英国 · 伦敦", "tz": "Europe/London", "flag": "🇬🇧"},
                {"name": "爱尔兰 · 都柏林", "tz": "Europe/Dublin", "flag": "🇮🇪"},
                {"name": "葡萄牙 · 里斯本", "tz": "Europe/Lisbon", "flag": "🇵🇹"},
                {"name": "挪威 · 奥斯陆", "tz": "Europe/Oslo", "flag": "🇳🇴"},
                {"name": "瑞典 · 斯德哥尔摩", "tz": "Europe/Stockholm", "flag": "🇸🇪"},
                {"name": "丹麦 · 哥本哈根", "tz": "Europe/Copenhagen", "flag": "🇩🇰"},
                {"name": "荷兰 · 阿姆斯特丹", "tz": "Europe/Amsterdam", "flag": "🇳🇱"},
                {"name": "比利时 · 布鲁塞尔", "tz": "Europe/Brussels", "flag": "🇧🇪"},
                {"name": "法国 · 巴黎", "tz": "Europe/Paris", "flag": "🇫🇷"},
                {"name": "瑞士 · 苏黎世", "tz": "Europe/Zurich", "flag": "🇨🇭"},
                {"name": "德国 · 柏林", "tz": "Europe/Berlin", "flag": "🇩🇪"},
                {"name": "奥地利 · 维也纳", "tz": "Europe/Vienna", "flag": "🇦🇹"},
                {"name": "捷克 · 布拉格", "tz": "Europe/Prague", "flag": "🇨🇿"},
                {"name": "波兰 · 华沙", "tz": "Europe/Warsaw", "flag": "🇵🇱"},
                {"name": "匈牙利 · 布达佩斯", "tz": "Europe/Budapest", "flag": "🇭🇺"},
                {"name": "克罗地亚 · 萨格勒布", "tz": "Europe/Zagreb", "flag": "🇭🇷"},
                {"name": "西班牙 · 马德里", "tz": "Europe/Madrid", "flag": "🇪🇸"},
                {"name": "意大利 · 罗马", "tz": "Europe/Rome", "flag": "🇮🇹"}
            ],
            "🏛️ 东欧时间 (EET) / 欧洲其它节点": [
                {"name": "芬兰 · 赫尔辛基", "tz": "Europe/Helsinki", "flag": "🇫🇮"},
                {"name": "保加利亚 · 索非亚", "tz": "Europe/Sofia", "flag": "🇧🇬"},
                {"name": "希腊 · 雅典", "tz": "Europe/Athens", "flag": "🇬🇷"},
                {"name": "俄罗斯 · 莫斯科", "tz": "Europe/Moscow", "flag": "🇷🇺"},
                {"name": "乌克兰 · 基辅", "tz": "Europe/Kyiv", "flag": "🇺🇦"},
                {"name": "土耳其 · 伊斯坦布尔", "tz": "Europe/Istanbul", "flag": "🇹🇷"}
            ],
            "🕌 中东 & 🌍 非洲节点": [
                {"name": "伊朗 · 德黑兰", "tz": "Asia/Tehran", "flag": "🇮🇷"},
                {"name": "以色列 · 耶路撒冷", "tz": "Asia/Jerusalem", "flag": "🇮🇱"},
                {"name": "沙特 · 利雅得", "tz": "Asia/Riyadh", "flag": "🇸🇦"},
                {"name": "阿联酋 · 迪拜", "tz": "Asia/Dubai", "flag": "🇦🇪"},
                {"name": "摩洛哥 · 卡萨布兰卡", "tz": "Africa/Casablanca", "flag": "🇲🇦"},
                {"name": "埃及 · 开罗", "tz": "Africa/Cairo", "flag": "🇪🇬"},
                {"name": "尼日利亚 · 拉各斯", "tz": "Africa/Lagos", "flag": "🇳🇬"},
                {"name": "南非 · 约翰内斯堡", "tz": "Africa/Johannesburg", "flag": "🇿🇦"}
            ],
            "🥢 亚洲核心测试节点": [
                {"name": "日本 · 东京", "tz": "Asia/Tokyo", "flag": "🇯🇵"},
                {"name": "韩国 · 首尔", "tz": "Asia/Seoul", "flag": "🇰🇷"},
                {"name": "中国 · 上海", "tz": "Asia/Shanghai", "flag": "🇨🇳"},
                {"name": "中国 · 香港", "tz": "Asia/Hong_Kong", "flag": "🇭🇰"},
                {"name": "巴基斯坦 · 卡拉奇", "tz": "Asia/Karachi", "flag": "🇵🇰"},
                {"name": "孟加拉国 · 达卡", "tz": "Asia/Dhaka", "flag": "🇧🇩"},
                {"name": "印度 · 加尔各答", "tz": "Asia/Kolkata", "flag": "🇮🇳"},
                {"name": "泰国 · 曼谷", "tz": "Asia/Bangkok", "flag": "🇹🇭"},
                {"name": "越南 · 胡志明市", "tz": "Asia/Ho_Chi_Minh", "flag": "🇻🇳"},
                {"name": "菲律宾 · 马尼拉", "tz": "Asia/Manila", "flag": "🇵🇭"},
                {"name": "马来西亚 · 吉隆坡", "tz": "Asia/Kuala_Lumpur", "flag": "🇲🇾"},
                {"name": "新加坡 · 新加坡", "tz": "Asia/Singapore", "flag": "🇸🇬"},
                {"name": "印度尼西亚 · 雅加达", "tz": "Asia/Jakarta", "flag": "🇮🇩"}
            ]
        }
        main_col1, main_col2 = st.columns(2)
        utc_now = datetime.fromtimestamp(time.time(), pytz.utc)

        def render_region_block(title, nodes):
            html_buffer = f"""<div style="background-color: #1a1a1a; padding: 15px; border-radius: 8px; border: 1px solid #2d2d2d; margin-bottom: 20px;">
<div style="font-size: 16px; font-weight: bold; color: #ffffff; border-bottom: 2px solid #339af0; padding-bottom: 5px; margin-bottom: 12px;">{title}</div>
<div style="display: grid; grid-template-columns: 1fr; gap: 10px; font-family: monospace;">"""
            for node in nodes:
                try:
                    local_time = utc_now.astimezone(pytz.timezone(node["tz"]))
                    day_str, time_str = local_time.strftime("%d"), local_time.strftime("%H:%M")
                    is_shanghai = "上海" in node["name"]
                    bg_style = 'background-color: #2b2b2b; border-radius: 4px; padding: 4px 6px;' if is_shanghai else ''
                    text_color = '#ff922b' if is_shanghai else '#adb5bd'
                    html_buffer += f"""<div style="display: flex; justify-content: space-between; align-items: center; font-size: 14px; {bg_style}">
<div style="color: #ffffff; display: flex; align-items: flex-start; flex-direction: column; gap: 2px;">
<div style="display: flex; align-items: center; gap: 6px;"><span>{node["flag"]}</span><span style="font-weight: 500; color: #ffffff;">{node["name"]}</span></div>
<span style="font-size: 11px; color: #666666; padding-left: 24px; font-family: Consolas, monospace;">{node["tz"]}</span>
</div>
<div style="display: flex; align-items: center; gap: 8px;">
<span style="background-color: #ff922b; color: #ffffff; font-size: 10px; padding: 1px 4px; border-radius: 3px; font-weight: bold;">{day_str}日</span>
<span style="color: {text_color}; font-weight: bold; font-size: 15px;">{time_str}</span>
</div>
</div>"""
                except Exception:
                    continue
            return (html_buffer + "</div></div>").strip()

        with main_col1:
            st.markdown(render_region_block("🌎 美洲核心业务节点", regions_data["🌎 美洲节点"]), unsafe_allow_html=True)
            st.markdown(render_region_block("🌊 太平洋/大洋洲节点", regions_data["🌊 太平洋节点"]),
                        unsafe_allow_html=True)
            st.markdown(render_region_block("🇪🇺 西欧时间 (WET) / 中欧时间 (CET)",
                                            regions_data["🇪🇺 西欧时间 (WET) / 中欧时间 (CET)"]), unsafe_allow_html=True)
        with main_col2:
            # 🔥【核心修复点】：将 "EET) / 俄罗斯" 改为 "EET) / 欧洲其它节点"
            st.markdown(render_region_block("🏛️ 东欧时间 (EET) / 欧洲其它节点",
                                            regions_data["🏛️ 东欧时间 (EET) / 欧洲其它节点"]), unsafe_allow_html=True)

            st.markdown(render_region_block("🕌 中东 & 🌍 非洲主要测试节点", regions_data["🕌 中东 & 🌍 非洲节点"]),
                        unsafe_allow_html=True)
            st.markdown(render_region_block("🥢 亚洲出海高频测试节点", regions_data["🥢 亚洲核心测试节点"]),
                        unsafe_allow_html=True)

        if st.button("⚡ 强制刷新全球时钟状态", key="btn_refresh_world_time", type="primary",
                     use_container_width=True): st.rerun()