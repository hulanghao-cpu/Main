import streamlit as st
import requests
import urllib.parse
import json


def render_account_view():
    env_selection = "🔥 正式环境 (Prod)" if st.session_state.is_prod else "🧪 测试环境 (Test)"
    st.subheader(f"👤 [{env_selection}] 设备查询与账号运维")

    tab_account_manage, tab_register_ip, tab_whitelist, tab_ip_lookup, tab_reset_device = st.tabs([
        "🔍 用户查询与销户", "🌍 修改用户注册 IP", "🛡️ 白名单权限控制", "🌐 IP 批量地理位置查询", "♻️ 设备数据与时区重置"
    ])

    is_prod = st.session_state.is_prod
    current_token = st.session_state.prod_token if is_prod else st.session_state.test_token
    pub_url = "https://v-adm.crazymaplestudios.com" if is_prod else "https://test-v-adm.stardustworld.cn"

    common_headers = {
        "Authorization": str(current_token), "appid": "cm1009", "Accept": "*/*",
        "Accept-Language": "zh-CN,zh;q=0.9", "cache-control": "no-cache", "pragma": "no-cache",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    if is_prod:
        common_headers["Origin"] = "https://v-adm.crazymaplestudios.com"
        common_headers["Referer"] = "https://v-adm.crazymaplestudios.com/app-user-manage/user-list"
        common_headers["content-referer"] = "https://v-adm.crazymaplestudios.com/app-user-manage/user-list"
    else:
        common_headers["Origin"] = "https://test-v-adm.stardustworld.cn"
        common_headers["Referer"] = "https://test-v-adm.stardustworld.cn/app-user-manage/user-list"

    prod_strict_headers = {
        "accept": "*/*", "accept-language": "zh-CN,zh;q=0.9", "appid": "cm1009",
        "authorization": str(current_token).strip(),
        "cache-control": "no-cache", "content-referer": "https://v-adm.crazymaplestudios.com/app-user-manage/user-list",
        "pragma": "no-cache", "referer": "https://v-adm.crazymaplestudios.com/app-user-manage/user-list",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Cookie": "acw_tc=ac15b34d17834092266045932e1f0062a66def6c69db666f956e9bb4544e2e"
    }

    with tab_account_manage:
        st.markdown("### 🔍 用户及设备信息高级反查 (User Inspector)")
        st.caption("集成统一的 member 网关，支持按设备标识或指定 UID/账号状态/登录方式进行精准多维反查。")

        # 1. 顶部提供原汁原味的查询方式切换
        search_mode = st.radio(
            "查询方式：",
            ["按设备 ID / 模型查询", "按 UID 查询"],
            horizontal=True,
            key="tab1_search_mode_global"
        )

        st.markdown("#### ⚙️ 统一检索过滤特征")
        col_in1, col_in2 = st.columns(2)
        with col_in1:
            # ustatus: 账号状态 0为启用 1为封禁 2为注销
            ustatus_label = st.selectbox(
                "🔒 账号状态过滤 (ustatus):",
                options=["🟢 启用 (0)", "🚫 封禁 (1)", "❌ 注销 (2)"],
                index=0,
                key="tab1_inspect_ustatus"
            )
            ustatus_val = "0" if "启用" in ustatus_label else ("1" if "封禁" in ustatus_label else "2")

        with col_in2:
            # 1. 声明下拉选择框，将 “✨ 不限（不传该参数）” 挂载在最前面作为默认选项 (index=0)
            sid_label = st.selectbox(
                "🔑 登录方式过滤 (sid):",
                options=[
                    "✨ 不限（不传该参数）",
                    "👤 游客登录 (0)",
                    "🍏 Apple 登录 (1)",
                    "✉️ 邮箱登录 (2)",
                    "💬 Facebook 登录 (3)"
                ],
                index=0,
                key="tab1_inspect_sid"
            )

            # 2. 🧬【核心映射重构】：根据用户选择，精准推导 sid 的实际参数值
            if "不限" in sid_label:
                sid_val = None  # 👈 赋值为 None，代表彻底不传递该参数
            elif "游客" in sid_label:
                sid_val = "0"
            elif "Apple" in sid_label:
                sid_val = "1"
            elif "邮箱" in sid_label:
                sid_val = "2"
            else:
                sid_val = "3"

        st.markdown("---")

        # 2. 核心分支流切换：模式 A (按设备查询)
        if search_mode == "按设备 ID / 模型查询":
            # 🟢 🔥【核心修改点】：让正式环境和测试环境一样，可以选择常用的 Android 和 iOS 测试机
            if is_prod:
                device_options = {
                    "Android 测试机 (c29d...)": "c29dbebf292b9aa4",
                    "iOS 测试机 (68DC...)": "68DCDBAA-8153-45C8-9B93-B0BB45589161",
                    "自定义设备模型 (dev_model)": "custom"
                }
            else:
                device_options = {
                    "Android 测试机 (c29d...)": "c29dbebf292b9aa4",
                    "iOS 测试机 (68DC...)": "68DCDBAA-8153-45C8-9B93-B0BB45589161",
                    "自定义设备 ID": "custom"
                }

            selected_label = st.selectbox("选择目标测试设备：", list(device_options.keys()), key="tab1_dev_select")

            # 判断是否需要手动输入
            dev_id = st.text_input("请输入自定义设备模型/ID：", key="tab1_custom_dev") if selected_label in [
                "自定义设备模型 (dev_model)", "自定义设备 ID"] else device_options[selected_label]

            search_trigger = st.button("查询用户信息", type="primary", key="tab1_search_dev_btn",
                                       use_container_width=True)

            if search_trigger:
                if not dev_id.strip():
                    st.error("❌ 错误：设备 ID / 模型不能为空！")
                else:
                    with st.spinner("正在获取用户信息..."):
                        try:
                            param_key = "dev_id"
                            clean_dev_id = dev_id.strip()

                            # 1️⃣ 🎯【动态字典构建】：将必须传递的固定参数初始化进字典
                            # 注意：这里去掉了硬编码的字符串拼接，改用 Requests 的标准 params 传参
                            inspect_params = {
                                "uid": "",
                                param_key: clean_dev_id,
                                "page": 1 if not is_prod else "1",  # 维持你原代码正式服字符串、测试服整型的微小习惯
                                "page_size": 20 if not is_prod else "20"
                            }

                            # 2️⃣ 🎯【按需挂载】：只有当过滤参数不为 None 时，才往字典里塞
                            if 'ustatus_val' in locals() and ustatus_val is not None:
                                inspect_params["ustatus"] = ustatus_val
                            elif 'ustatus_val' not in locals():
                                # 兜底：如果外部没有声明 ustatus_val 变量，尝试看看前端组件是否有对应值，没有则直接不传
                                pass

                            if sid_val is not None:
                                inspect_params["sid"] = sid_val  # 👈 如果选了“不限”，sid_val为None，这行就不会执行，参数完美剥离！

                            # 3️⃣ 🎯【动态环境适配】：剥离 URL 中的 Query 尾巴，只留纯净的 Base URL
                            if is_prod:
                                base_url = "https://v-adm.crazymaplestudios.com/api/member"
                                inspect_headers = prod_strict_headers
                            else:
                                base_url = f"{pub_url}/api/member"
                                inspect_headers = common_headers

                            # 4️⃣ 🎯【物理级最终 URL 预览】：为了让你底部的 Inspector 透视面板能准确看到被剃光后的 URL
                            from requests.models import PreparedRequest
                            req_obj = PreparedRequest()
                            req_obj.prepare_url(base_url, inspect_params)
                            final_preview_url = req_obj.url  # 这里的网址会自动对 dev_id 做完美的 URL 编码，且自动去掉了 None 参数

                            # 压入前端底部的 HTTP 透视面板（Request Inspector）
                            st.session_state["tab1_inspect_data"] = {
                                "url": final_preview_url,
                                "headers": inspect_headers,
                                "params": inspect_params
                            }

                            # 5️⃣ 🎯【安全发射】：改用标准的 params= 参数传递
                            res = requests.get(url=base_url, params=inspect_params, headers=inspect_headers, timeout=10)

                            # 6️⃣ 🎯【业务状态分流判定】：维持你原有的高强壮度数据解析机制
                            if res.status_code == 200 and res.json().get("code") in [0, 200]:
                                collections = res.json().get("data", {}).get("collections", [])
                                if collections:
                                    st.session_state["cache_tab1_user_info"] = collections[0]
                                    st.session_state.search_uid = str(collections[0].get("uid"))
                                    st.success("🎯 设备关联用户数据锁定成功！")
                                    st.rerun()
                                else:
                                    st.session_state["cache_tab1_user_info"] = None
                                    st.warning(f"⚠️ 接口响应成功，但在当前过滤特征下，{param_key} 未匹配到任何激活账号。")
                            elif res.status_code == 401:
                                st.error(
                                    "❌ 401 Unauthorized：正式服 Token 已失效，请前往【🔑 登录认证助手】重新登录刷新凭证！")
                                st.session_state["cache_tab1_user_info"] = None
                            else:
                                st.error(f"❌ 查询失败: {res.text}")
                                st.session_state["cache_tab1_user_info"] = None
                        except Exception as e:
                            st.error(f"💥 网络透传异常: {e}")
                            st.session_state["cache_tab1_user_info"] = None

        # 3. 核心分支流切换：模式 B (按 UID 查询)
        else:
            input_query_uid = st.text_input("输入要核对的 UID:", value=st.session_state.search_uid,
                                            key="tab1_query_uid_input")
            # 同步更新全局状态锁
            st.session_state.search_uid = input_query_uid

            if st.button("核对用户信息", type="primary", key="tab1_search_uid_btn", use_container_width=True):
                with st.spinner("正在核对用户信息..."):
                    try:
                        if is_prod:
                            # 正式服完美复刻抓包报文的统一传参格式
                            inspect_url = f"https://v-adm.crazymaplestudios.com/api/member?uid={str(input_query_uid).strip()}&ustatus={ustatus_val}&sid={sid_val}&page=1&page_size=20&secret=2024062716138845"
                            inspect_headers = prod_strict_headers
                            inspect_params = {"uid": str(input_query_uid).strip(), "ustatus": ustatus_val,
                                              "sid": sid_val, "page": "1", "page_size": "20",
                                              "secret": "2024062716138845"}
                        else:
                            inspect_url = f"{pub_url}/api/member?uid={str(input_query_uid).strip()}&ustatus={ustatus_val}&sid={sid_val}&page=1&page_size=20"
                            inspect_headers = common_headers
                            inspect_params = {"uid": str(input_query_uid).strip(), "ustatus": ustatus_val,
                                              "sid": sid_val, "page": 1, "page_size": 20}

                        st.session_state["tab1_inspect_data"] = {"url": inspect_url, "headers": inspect_headers,
                                                                 "params": inspect_params}

                        res = requests.get(url=inspect_url, headers=inspect_headers, timeout=10)
                        if res.status_code == 200 and res.json().get("code") in [0, 200]:
                            collections = res.json().get("data", {}).get("collections", [])
                            if collections:
                                st.session_state["cache_tab1_user_info"] = collections[0]
                                st.session_state.search_uid = str(collections[0].get("uid"))
                                st.rerun()
                            else:
                                st.session_state["cache_tab1_user_info"] = None
                                st.warning("⚠️ 未找到该筛选条件下的 UID 账号信息")
                        else:
                            st.error(f"❌ 核对失败: {res.text}")
                    except Exception as e:
                        st.error(f"网络异常: {e}")

        # 4. 数据落地持久化看盘与危险销户区（完全继承原版）
        st.markdown("---")
        if st.session_state["cache_tab1_user_info"] is not None:
            user_info_verified = st.session_state["cache_tab1_user_info"]
            col_tl, col_tr = st.columns([7, 3])
            with col_tl:
                st.success("🎯 用户核对数据获取成功！（已锁定呈现）")
            with col_tr:
                if st.button("🧹 清除查询记录", key="clear_u_cache", use_container_width=True):
                    st.session_state["cache_tab1_user_info"] = None
                    st.session_state["tab1_inspect_data"] = None
                    st.rerun()

            col_info1, col_info2, col_info3 = st.columns(3)
            with col_info1:
                st.metric("用户 UID", user_info_verified.get("uid"))
            with col_info2:
                st.metric("渠道 ID", user_info_verified.get("channel_id", "未知"))
            with col_info3:
                st.metric("设备标识",
                          str(user_info_verified.get("dev_model") if is_prod else user_info_verified.get("dev_id")))

            with st.expander("📄 查看完整原始返回 JSON 数据"):
                st.json(user_info_verified)

            st.markdown("### 🔥 危险操作：删除账号")
            uid_to_del = st.text_input("确认为最终要删除 the UID:", value=str(user_info_verified.get("uid")),
                                       key="tab1_uid_input_secure")
            confirm_del = st.checkbox("确定删除该账号（不可逆）！", key="tab1_confirm_secure")
            if st.button("立即执行销户", type="secondary", key="tab1_del_btn_secure"):
                if confirm_del and uid_to_del:
                    with st.spinner("正在销户..."):
                        try:
                            headers = {"authorization": current_token, "content-type": "application/json;charset=UTF-8",
                                       "appid": "cm1009"}
                            re = requests.post(url=f"{pub_url}/api/member/delete", headers=headers,
                                               json={"uid": int(uid_to_del)}, timeout=10)
                            st.success("销户请求已提交，请查看底部 Inspector 返回！")
                            st.session_state["cache_tab1_user_info"] = None
                            st.rerun()
                        except Exception as e:
                            st.error(f"异常: {e}")
        else:
            st.info("💡 暂无激活的查询看板。请输入设备或 UID 查验后在此锁定。")

    with tab_register_ip:
        st.markdown("### 🌍 模拟跨境：修改指定用户的初始注册地区 IP")
        ip_target_uid = st.text_input("要修改的注册 user UID:", value=st.session_state.search_uid, key="tab1_ip_uid")
        country_presets = {
            "T1 - 新加坡 (sg)": {"country": "sg", "ip": "121.7.255.255"},
            "T2 - 德国 (de)": {"country": "de", "ip": "104.28.156.3"},
            "T3 - 阿根廷 (ar)": {"country": "ar", "ip": "190.31.255.255"},
            "T4 - 泰国 (th)": {"country": "th", "ip": "45.40.52.77"},
            "T5 - 印尼 (id)": {"country": "id", "ip": "103.213.128.147"},
            "✏️ 自定义输入地区与 IP": {"country": "custom", "ip": "custom"}
        }
        selected_preset = st.selectbox("请选择目标变更的国家层级 Presets:", list(country_presets.keys()),
                                       key="tab1_ip_preset_select")
        if selected_preset == "✏️ 自定义输入地区与 IP":
            target_country = st.text_input("请输入目标国家代码 (小写):", value="us", key="tab1_ip_custom_country")
            target_ip = st.text_input("请输入特定的目标国家 IP 地址:", value="8.222.248.114", key="tab1_ip_custom_ip")
        else:
            target_country = country_presets[selected_preset]["country"]
            target_ip = country_presets[selected_preset]["ip"]
            st.info(f"📋 当前锁定目标 -> 国家代号: `{target_country.upper()}` | 绑定 IP: `{target_ip}`")

        with st.expander("⚙️ 签名高级鉴权选项"):
            ip_secret = st.text_input("URL 安全密钥 (secret):", value="2024062716138845", key="tab1_ip_secret")
            ip_sign = st.text_input("防篡改签名密文 (sign):",
                                    value="aff3be2c8856f5c64729fb1d2c8209670a77c685398ad803c7838bac2198e248",
                                    key="tab1_ip_sign")
            ip_ts = st.text_input("请求时间戳 (ts):", value="1592993199", key="tab1_ip_ts")
            ip_session = st.text_input("当前活跃会话 (session):", value="6f7e07619de19fa00390f47a126d2ff8",
                                       key="tab1_ip_session")

        st.markdown("---")
        if st.button("🚀 立即修改注册 IP 归属地", type="primary", key="tab1_ip_submit_btn"):
            with st.spinner("正在提交重写指令..."):
                ip_base_url = "https://gray-v-api.stardustgod.com" if is_prod else "https://dev-project-v-api.stardustworld.cn"
                ip_query_url = f"{ip_base_url}/api/test/updateRegisterIp?secret={ip_secret.strip()}&country={target_country.strip()}&ip={target_ip.strip()}"
                ip_headers = {
                    "uid": str(ip_target_uid).strip(), "channelId": "AVG20001", "ts": str(ip_ts).strip(),
                    "apiVersion": "1.0.0", "session": str(ip_session).strip(), "lang": "en",
                    "sign": str(ip_sign).strip(),
                    "clientVer": "1.0.5", "Accept": "application/json", "Content-Type": "application/json;charset=UTF-8"
                }
                try:
                    ip_response = requests.post(url=ip_query_url, headers=ip_headers, timeout=15)
                    st.session_state["cache_tab1_ip_res"] = {"code": ip_response.status_code, "text": ip_response.text}
                    st.session_state["tab1_inspect_data"] = {"url": ip_query_url, "headers": ip_headers,
                                                             "params": {"secret": ip_secret, "country": target_country,
                                                                        "ip": target_ip}}
                except Exception as e:
                    st.error(f"❌ 网络异常: {e}")

        if st.session_state["cache_tab1_ip_res"] is not None:
            res_data = st.session_state["cache_tab1_ip_res"]
            st.markdown("### 📥 归属地修改接口返回结果")
            st.code(f"状态码: {res_data['code']}\n返回明文: {res_data['text']}")
            if res_data['code'] == 200: st.success("🎉 注册 IP 修改指令分发成功！")

    with tab_whitelist:
        st.markdown("### 🛡️ 灰度测试机与设备白名单控制面板")
        wl_device_presets = {"iOS 稳定灰度测试机": "68DCDBAA-8153-45C8-9B93-B0BB45589161",
                             "✏️ 手动输入指定设备 devId": "custom"}
        selected_wl_preset = st.selectbox("选择或代入目标测试设备:", list(wl_device_presets.keys()),
                                          key="tab1_wl_preset_select")
        wl_dev_id = st.text_input("请输入目标设备的真实 devId:", value="",
                                  key="tab1_wl_custom_devid") if selected_wl_preset == "✏️ 手动输入指定设备 devId" else \
        wl_device_presets[selected_wl_preset]

        type_dictionary = {
            "1️⃣ 中国 IP、中国运营商 封禁白名单 (type=1)": 1, "2️⃣ APP 可以设置中文语言白名单 (type=2)": 2,
            "3️⃣ 互动剧视频质检白名单 (type=3)": 3, "4️⃣ iOS 录屏白名单 (type=4)": 4,
            "5️⃣ PC 端观看完整剧集白名单 (type=5)": 5
        }
        selected_type_label = st.selectbox("请选择白名单对应的业务类型 (type):", list(type_dictionary.keys()), index=1,
                                           key="tab1_wl_type_select")
        wl_type = type_dictionary[selected_type_label]

        wl_action_mapping = {"➕ 将该设备加入内部白名单 (放行)": 1, "➖ 将该设备移出内部白名单 (退白)": 0}
        selected_wl_action_label = st.radio("请指定白名单执行动作 (action):", list(wl_action_mapping.keys()),
                                            horizontal=True, key="tab1_wl_action_radio")
        wl_action = wl_action_mapping[selected_wl_action_label]

        with st.expander("⚙️ 白名单底层特征配置 center"):
            wl_secret = st.text_input("白名单控制密钥 (secret):", value="2024062716138845", key="tab1_wl_secret")
            wl_append_break = st.checkbox("在 devId 尾部严格附加 cURL 换行符 (\\n)", value=True,
                                          key="tab1_wl_append_break")

        st.markdown("---")
        if st.button("🚀 提请执行白名单变更", key="tab1_wl_submit_btn",
                     type="primary" if wl_action == 1 else "secondary"):
            if not wl_dev_id:
                st.error("❌ 设备 devId 不能为空！")
            else:
                with st.spinner("正在处理白名单分发..."):
                    wl_base_url = "https://v-adm.stardustgod.com" if is_prod else "https://test-v-adm.stardustworld.cn"
                    final_dev_id = wl_dev_id.strip() + "\n" if wl_append_break else wl_dev_id.strip()
                    encoded_dev_id = urllib.parse.quote(final_dev_id)
                    wl_query_url = f"{wl_base_url}/api/test/whiteListAction?secret={wl_secret.strip()}&type={int(wl_type)}&action={int(wl_action)}&devId={encoded_dev_id}"
                    wl_headers = {"User-Agent": "Mozilla/5.0", "Accept": "*/*"}
                    if is_prod: wl_headers["authorization"] = str(current_token).strip()

                    try:
                        wl_res = requests.get(url=wl_query_url, headers=wl_headers, timeout=10)
                        st.session_state["cache_tab1_wl_res"] = {"code": wl_res.status_code, "text": wl_res.text}
                        st.session_state["tab1_inspect_data"] = {"url": wl_query_url, "headers": wl_headers,
                                                                 "params": {"secret": wl_secret, "type": int(wl_type),
                                                                            "action": int(wl_action),
                                                                            "devId": final_dev_id}}
                    except Exception as e:
                        st.error(f"❌ 请求异常: {e}")

        if st.session_state["cache_tab1_wl_res"] is not None:
            wl_data = st.session_state["cache_tab1_wl_res"]
            st.markdown("### 📥 白名单接口返回结果")
            st.code(f"状态码: {wl_data['code']}\n返回报文: {wl_data['text']}")
            if wl_data['code'] == 200: st.success("🎉 白名单策略配置已下发完毕！")

    with tab_ip_lookup:
        import re
        st.markdown("### 🌐 IP 批量地理位置反查中心")
        col_p1, col_p2, col_p3 = st.columns(3)
        with col_p1:
            if st.button("🌟 代入示例 cURL IP 对", key="btn_preset_demo"): st.session_state[
                "tab1_ip_textarea"] = "121.7.255.255"
        with col_p2:
            if st.button("🚀 代入 T1-T5 海外测试 IP", key="btn_preset_t15"): st.session_state[
                "tab1_ip_textarea"] = "121.7.255.255\n104.28.156.3\n190.31.255.255\n45.40.52.77\n103.213.128.147"
        with col_p3:
            if st.button("🧹 清空输入框", key="btn_preset_clear"): st.session_state["tab1_ip_textarea"] = ""

        ip_input_raw = st.text_area("请在下方输入待查询的 IP 地址：", value=st.session_state.get("tab1_ip_textarea", ""),
                                    height=150, key="tab1_ip_textarea")

        st.markdown("---")
        if st.button("🔍 立即执行批量地理位置反查", type="primary", key="tab1_ip_lookup_submit_btn"):

            ip_list = re.findall(r'(?:[0-9]{1,3}\.){3}[0-9]{1,3}', ip_input_raw)
            if not ip_list:
                st.error("❌ 未在输入框中解析出任何合法的 IPv4 地址！")
            # ... 后续逻辑保持不变 ...
            else:
                with st.spinner("正在向网关反查地理位置..."):
                    batch_url = "http://ip-api.com/batch"
                    try:
                        response = requests.post(url=batch_url, headers={"Content-Type": "application/json"},
                                                 data=json.dumps(ip_list), timeout=15)
                        if response.status_code == 200:
                            st.session_state["cache_tab1_lookup_res"] = response.json()
                            st.session_state["tab1_inspect_data"] = {"url": batch_url,
                                                                     "headers": {"Content-Type": "application/json"},
                                                                     "params": {"Payload_Body": ip_list}}
                        else:
                            st.error(f"网关错误: {response.status_code}")
                    except Exception as e:
                        st.error(f"❌ 异常: {e}")

        if st.session_state["cache_tab1_lookup_res"] is not None:
            res_json = st.session_state["cache_tab1_lookup_res"]
            st.success("🎉 批量解析完成！")
            import pandas as pd
            df_rows = []
            for item in res_json:
                if item.get("status") == "success":
                    df_rows.append({
                        "🔍 目标 IP": item.get("query"), "🌍 国家": f"{item.get('country')} ({item.get('countryCode')})",
                        "📍 省份": item.get("regionName"), "🏙️ 城市": item.get("city"), "🏢 运营商 (ISP)": item.get("isp")
                    })
            st.dataframe(pd.DataFrame(df_rows), use_container_width=True)

    with tab_reset_device:
        st.markdown("### ♻️ 一键清理设备数据与时区重置")
        st.markdown(
            "调用底层 `dleDeviceData` 高阶测试接口，可以极速对齐指定测试机的时区，清除其三方留存，并重置其专属签到进度。")
        st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)

        col_res1, col_res2 = st.columns(2)
        with col_res1:
            dev_id_presets_unique = {"iOS 默认灰度测试机 (68DC...)": "68DCDBAA-8153-45C8-9B93-B0BB45589161",
                                     "Android 测试机 (c29d...)": "c29dbebf292b9aa4",
                                     "✏️ 手动输入指定设备 devId": "custom"}
            selected_res_dev = st.selectbox("1. 选择目标测试设备 (devId/模型):", list(dev_id_presets_unique.keys()),
                                            key="tab1_res_dev_sel_unique")
            final_res_devId = st.text_input("请输入特定的设备 ID:", value="",
                                            key="tab1_res_custom_dev_input") if selected_res_dev == "✏️ 手动输入指定设备 devId" else \
            dev_id_presets_unique[selected_res_dev]

            if st.button("🔍 通过该设备反查其绑定 UID", key="btn_lookup_uid_for_reset", use_container_width=True):
                if not final_res_devId:
                    st.error("❌ 设备 ID 不能为空，无法反查！")
                elif not current_token:
                    st.error("❌ 请先在左侧侧边栏配置 Token！")
                else:
                    with st.spinner("正在通过设备指纹追溯 UID..."):
                        # 🟢【路径防反斜杠报错修复】：提取外部硬拼接
                        tab_suffix = '\t'
                        full_dev_string = final_res_devId + tab_suffix
                        encoded_dev_model = urllib.parse.quote(full_dev_string)

                        if is_prod:
                            inspect_url = f"https://v-adm.crazymaplestudios.com/api/member?uid=&dev_model={encoded_dev_model}&page=1&page_size=20&secret=2024062716138845"
                            inspect_headers = prod_strict_headers
                            res = requests.get(url=inspect_url, headers=inspect_headers, timeout=10)
                        else:
                            inspect_url = f"{pub_url}/api/member"
                            inspect_headers = common_headers
                            inspect_params = {"sid": 0, "dev_id": str(final_res_devId), "ustatus": 0, "uname": "Guest"}
                            res = requests.get(inspect_url, headers=inspect_headers, params=inspect_params, timeout=10)

                        try:
                            if res.status_code == 200 and res.json().get("code") in [0, 200]:
                                collections = res.json().get("data", {}).get("collections", [])
                                if collections:
                                    found_uid = str(collections[0].get("uid"))
                                    st.session_state.search_uid = found_uid
                                    st.toast(f"🎯 成功追溯到 UID: {found_uid} 并已自动填入右侧！", icon="✅")
                                    st.rerun()
                                else:
                                    st.warning("⚠️ 该设备未绑定任何激活账号。")
                            else:
                                st.error(f"❌ 反查失败，接口回执: {res.text}")
                        except Exception as parse_err:
                            st.error(f"❌ 接口请求解析异常: {parse_err}")

        with col_res2:
            final_res_uid = st.text_input("2. 目标重置用户 UID (支持手动编辑或从左侧反查):",
                                          value=st.session_state.search_uid, key="tab1_res_uid_input_unique_field")
            if final_res_uid != st.session_state.search_uid: st.session_state.search_uid = final_res_uid

        st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
        col_res3, col_res4, col_res5 = st.columns([4, 4, 2])
        with col_res3:
            timezone_options_list = ["America/Los_Angeles (美国美西/洛杉矶时区)", "Asia/Shanghai (中国北京时间)",
                                     "Europe/London (英国伦敦时区)", "Asia/Singapore (新加坡时区)",
                                     "UTC (世界标准时间)", "✏️ 手动输入自定义时区 (Timezone ID)"]
            selected_res_tz_label = st.selectbox("3. 设定目标用户的时区 (time_zone):", timezone_options_list, index=0,
                                                 key="tab1_res_tz_sel_unique")
        with col_res4:
            if selected_res_tz_label == "✏️ 手动输入自定义时区 (Timezone ID)":
                final_res_tz = st.text_input("✒️ 请输入自定义时区 ID:", value="Asia/Tokyo",
                                             key="tab1_res_custom_tz_input_unique")
            else:
                final_res_tz = selected_res_tz_label.split(" ")[0]
                st.text_input("🔒 提取到的规范时区值:", value=final_res_tz, disabled=True,
                              key="tab1_res_tz_readonly_view_unique")
        with col_res5:
            res_refresh3rd = st.number_input("4. 三方专属签到重置:", value=1, step=1,
                                             key="tab1_res_refresh_input_unique")

        st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
        with st.expander("⚙️ 签名高级鉴权选项"):
            res_secret = st.text_input("控制网关密钥 (secret):", value="2024062716138845",
                                       key="tab1_res_secret_cfg_unique")
            res_sign = st.text_input("防篡改密文 (sign):",
                                     value="aff3be2c8856f5c64729fb1d2c8209670a77c685398ad803c7838bac2198e248",
                                     key="tab1_res_sign_cfg_unique")
            res_ts = st.text_input("鉴权时间戳 (ts):", value="1592993199", key="tab1_res_ts_cfg_unique")
            res_session = st.text_input("活跃会话标识 (session):", value="6f7e07619de19fa00390f47a126d2ff8",
                                        key="tab1_res_sess_cfg_unique")

        st.markdown("---")
        if st.button("🚀 立即执行一键清理并重置设备状态", type="primary", key="tab1_res_submit_btn_unique"):
            if not final_res_uid:
                st.error("❌ 目标 UID 不能为空，拒绝下发重置报文！")
            else:
                with st.spinner("正在下发全量清算重置报文..."):
                    res_base_url = "https://gray-v-api.stardustgod.com" if is_prod else "https://dev-project-v-api.stardustworld.cn"
                    res_full_url = f"{res_base_url}/api/test/dleDeviceData?secret={res_secret.strip()}"
                    res_headers = {
                        "devId": str(final_res_devId).strip(), "uid": str(final_res_uid).strip(),
                        "channelId": "AVG20001",
                        "ts": str(res_ts).strip(), "apiVersion": "1.4.8", "session": str(res_session).strip(),
                        "lang": "en", "sign": str(res_sign).strip(), "clientVer": "1.0.07",
                        "Content-Type": "application/json"
                    }
                    res_payload = {"time_zone": str(final_res_tz).strip(), "refresh3rd": int(res_refresh3rd)}
                    try:
                        response = requests.post(url=res_full_url, headers=res_headers, json=res_payload, timeout=15)
                        st.session_state["cache_tab1_reset_res"] = {"code": response.status_code, "text": response.text}
                        st.session_state["tab1_inspect_data"] = {"url": res_full_url, "headers": res_headers,
                                                                 "params": {"Query_Secret": res_secret,
                                                                            "POST_BODY_JSON": res_payload}}
                    except Exception as e:
                        st.error(f"❌ 异常: {e}")

        if st.session_state["cache_tab1_reset_res"] is not None:
            res_data = st.session_state["cache_tab1_reset_res"]
            st.markdown("### 📥 ♻️ 聚合网关响应结果 center")
            st.code(f"HTTP 状态码: {res_data['code']}\n返回明文: {res_data['text']}")
            if res_data['code'] == 200: st.success("🎉 设备留存数据与跨时区数据全量洗刷成功！")

    # if st.session_state["tab1_inspect_data"] is not None:
    #     st.markdown("---")
    #     inspect_cache = st.session_state["tab1_inspect_data"]
    #     st.markdown("### 🌐 HTTP 请求透视面板 (Request Inspector)")
    #     st.info(f"📍 **实际请求完整 URL:** `{inspect_cache['url']}`")
    #     ins_col1, ins_col2 = st.columns(2)
    #     with ins_col1:
    #         st.markdown("🔢 **Query / Body center**")
    #         st.json(inspect_cache["params"])
    #     with ins_col2:
    #         st.markdown("📋 **Headers**")
    #         st.json(inspect_cache["headers"])