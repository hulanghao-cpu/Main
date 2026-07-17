import streamlit as st
import requests
import json
import urllib.parse


def render_welfare_view():
    env_selection = "🔥 正式环境 (Prod)" if st.session_state.is_prod else "🧪 测试环境 (Test)"
    st.subheader(f"🎁 [{env_selection}] 用户专属福利页面任务配置查询")
    st.markdown("通过调用当前环境下的灰度福利网关实时读取指定用户的福利页关键规则、落库时区和任务列表。")

    is_prod = st.session_state.is_prod
    current_token = st.session_state.prod_token if is_prod else st.session_state.test_token
    pub_url = "https://v-adm.crazymaplestudios.com" if is_prod else "https://test-v-adm.stardustworld.cn"

    common_headers = {"Authorization": str(current_token), "appid": "cm1009", "Accept": "*/*",
                      "User-Agent": "Mozilla/5.0"}
    prod_strict_headers = {
        "accept": "*/*", "accept-language": "zh-CN,zh;q=0.9", "appid": "cm1009",
        "authorization": str(current_token).strip(),
        "content-referer": "https://v-adm.crazymaplestudios.com/app-user-manage/user-list", "pragma": "no-cache",
        "referer": "https://v-adm.crazymaplestudios.com/app-user-manage/user-list", "user-agent": "Mozilla/5.0"
    }

    st.markdown("### 📱 快捷设备指纹追溯")
    col_dev_l, col_dev_r = st.columns([7, 3])
    with col_dev_l:
        dev_id_presets_welfare = {"Android 测试机 (c29d...)": "c29dbebf292b9aa4",
                                  "iOS 默认灰度测试机 (68DC...)": "68DCDBAA-8153-45C8-9B93-B0BB45589161",
                                  "✏️ 手动输入指定设备 devId": "custom"}
        default_index = 0 if not is_prod else 1
        selected_wf_dev = st.selectbox("选择或输入当前抓包的测试设备 (devId/模型):",
                                       list(dev_id_presets_welfare.keys()), index=default_index, key="tab3_wf_dev_sel")
        final_wf_devId = st.text_input("请输入特定的设备 ID/模型:", value="",
                                       key="tab3_wf_custom_dev_input") if selected_wf_dev == "✏️ 手动输入指定设备 devId" else \
        dev_id_presets_welfare[selected_wf_dev]

    with col_dev_r:
        st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
        if st.button("🔍 通过设备反查 UID 并自动填充", key="btn_lookup_uid_for_welfare", use_container_width=True):
            if not final_wf_devId:
                st.error("❌ 设备 ID 不能为空！")
            elif not current_token:
                st.error("❌ 请先在左侧侧边栏配置对应环境的 Token！")
            else:
                with st.spinner("正在通过设备指纹反查对应的 UID..."):
                    if is_prod:
                        tab_suffix = b'\t'.decode('utf-8')
                        encoded_dev_model = urllib.parse.quote(final_wf_devId + tab_suffix)
                        inspect_url = f"https://v-adm.crazymaplestudios.com/api/member?uid=&dev_model={encoded_dev_model}&page=1&page_size=20&secret=2024062716138845"
                        res = requests.get(url=inspect_url, headers=prod_strict_headers, timeout=10)
                    else:
                        inspect_url = f"{pub_url}/api/member"
                        res = requests.get(inspect_url, headers=common_headers,
                                           params={"sid": 0, "dev_id": str(final_wf_devId), "ustatus": 0,
                                                   "uname": "Guest"}, timeout=10)

                    try:
                        if res.status_code == 200 and res.json().get("code") in [0, 200]:
                            collections = res.json().get("data", {}).get("collections", [])
                            if collections:
                                found_uid = str(collections[0].get("uid"))
                                st.session_state.search_uid = found_uid
                                st.toast(f"🎯 成功反查到 UID: {found_uid}，已注入下方表单！", icon="✅")
                                st.rerun()
                            else:
                                st.warning("⚠️ 该设备在当前环境下未绑定 any 账号。")
                        else:
                            st.error(f"❌ 反查请求失败: {res.text}")
                    except Exception as parse_err:
                        st.error(f"❌ 解析异常: {parse_err}")

    st.markdown("---")
    st.markdown("### ✏️ 目标用户与签名核心配置")
    reward_uid_mode = st.radio("UID 选择来源：", ["自动联动当前最新查询结果", "手动输入指定查询 UID"], horizontal=True,
                               key="reward_uid_mode_radio")

    with st.form(key="welfare_query_sandbox_form"):
        if reward_uid_mode == "自动联动当前最新查询结果":
            target_reward_uid = st.text_input("联动到的用户 UID:", value=st.session_state.search_uid,
                                              key="reward_linked_uid_in", disabled=True)
        else:
            target_reward_uid = st.text_input("请输入目标用户 UID:", value=st.session_state.search_uid,
                                              key="reward_manual_uid_in")

        st.markdown("#### 🔑 动态防刷签名与会话绑定（从最新抓包数据中复制）")
        col_sec1, col_sec2, col_sec3 = st.columns(3)
        with col_sec1:
            dynamic_sign = st.text_input("签名密文 (sign):",
                                         value="b31d1466f2eaeb66c4ee65fe530a66576b13bc1ae15eed0da967d7f9b3400f91",
                                         key="reward_dynamic_sign")
        with col_sec2:
            dynamic_ts = st.text_input("时间戳 (ts):", value="1783877657", key="reward_dynamic_ts")
        with col_sec3:
            dynamic_session = st.text_input("会话标识 (session):", value="2556c940602d95afc2d01313e663d153",
                                            key="reward_dynamic_session")

        st.markdown("#### 🔒 高级加密与行为鉴权字段")
        dynamic_req_time = st.text_area("加密请求时间戳 (requestTime):",
                                        value="81UVndRj34bJt4VVJXW3hIk4iCx1pG3fZ+py6RDg1HoC5ww4VqWHcB3BvEKdGbVM/2stUnZxBLNra654d5rQ5GJdBv9jjKHhW6SZHcaEbXs=",
                                        height=70, key="reward_dynamic_req_time")
        st.markdown("---")
        submit_clicked = st.form_submit_button("🔍 立即获取福利页配置", type="primary")

    if reward_uid_mode == "手动输入指定查询 UID" and target_reward_uid != st.session_state.search_uid:
        st.session_state.search_uid = target_reward_uid

    col_btn_l, col_btn_r = st.columns([7, 3])
    with col_btn_r:
        if st.session_state["cache_tab3_welfare_res"] is not None:
            if st.button("🧹 清除当前福利页查询记录", key="reward_clear_cache_btn", use_container_width=True):
                st.session_state["cache_tab3_welfare_res"] = None
                st.rerun()

    if submit_clicked:
        if not target_reward_uid:
            st.error("❌ 查询 UID 不能为空！")
        else:
            with st.spinner(f"正在向 {env_selection} 灰度福利网关发送拉取请求..."):
                if is_prod:
                    reward_url = "https://gray-v-api.crazymaplestudios.com/api/video/earn-reward/list?secret=2024062716138845"
                    reward_host = "gray-v-api.crazymaplestudios.com"
                    reward_referer = "https://gray-reward.reelshort.com/"
                    reward_dev_id = "68DCDBAA-8153-45C8-9B93-B0BB45589161"
                    reward_channel = "AVG20001"
                else:
                    reward_url = "https://dev-project-v-api.stardustworld.cn/api/video/earn-reward/list?secret=2024062716138845"
                    reward_host = "dev-project-v-api.stardustworld.cn"
                    reward_referer = "https://dev-project-v-api.stardustworld.cn/"
                    reward_dev_id = "c29dbebf292b9aa4"
                    reward_channel = "AVG10003"

                reward_headers = {
                    "Host": reward_host, "lang": "en", "Referer": reward_referer, "channelId": reward_channel,
                    "User-Agent": "Mozilla/5.0 (Linux; Android 16; SM-F731U1 Build/BP4A.251205.006; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/150.0.7871.46 Mobile Safari/537.36 InternalRSApp/4.0.00",
                    "ts": str(dynamic_ts).strip(), "session": str(dynamic_session).strip(),
                    "sign": str(dynamic_sign).strip(), "uid": str(target_reward_uid).strip(),
                    "apiVersion": "1.4.19", "clientVer": "4.0.00", "devId": reward_dev_id,
                    "requestTime": str(dynamic_req_time).strip(),
                    "Accept": "application/json, text/plain, */*",
                    "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
                    "timezone": "America/Los_Angeles", "time-zone": "-0800"
                }
                try:
                    response = requests.post(url=reward_url, headers=reward_headers, data={"is_web": "1"}, timeout=15)
                    st.session_state["cache_tab3_welfare_res"] = {"status_code": response.status_code,
                                                                  "text": response.text}
                    st.session_state["tab1_inspect_data"] = {"url": reward_url, "headers": reward_headers,
                                                             "params": {"is_web": 1, "target_uid": target_reward_uid,
                                                                        "env": env_selection}}
                except Exception as e:
                    st.error(f"❌ 请求异常: {e}")
            st.rerun()

    if st.session_state["cache_tab3_welfare_res"] is not None:
        welfare_cache = st.session_state["cache_tab3_welfare_res"]
        s_code = welfare_cache["status_code"]
        s_text = welfare_cache["text"]
        st.markdown("### 📥 接口原始返回结果")
        st.code(f"状态码: {s_code}\n返回报文: {s_text}")

        if s_code == 200:
            try:
                res_json = json.loads(s_text)
                if res_json.get("code") in [0, 200]:
                    st.success(f"🎉 [{env_selection}] 福利页面配置数据获取成功！")
                    data_block = res_json.get("data", {})
                    st.markdown("### 📊 关键配置高亮提取列表 center")
                    c_col1, c_col2, c_col3 = st.columns(3)
                    with c_col1:
                        st.metric("配置类型 (cfgType)", str(data_block.get("cfgType", "未返回")))
                    with c_col2:
                        st.metric("核心任务数 (task_num)", str(data_block.get("task_num", "未返回")))
                    with c_col3:
                        server_timezone = data_block.get("time_zone") or data_block.get("timeZone") or "未返回"
                        st.metric("用户落库时区 (time_zone)", str(server_timezone))

                    st.markdown("#### 📂 模块任务列表明细 (moduleList)")
                    modules = data_block.get("moduleList", [])
                    if modules:
                        st.json(modules)
                    else:
                        st.warning("⚠️ 接口返回的 moduleList 数据为空。")
                else:
                    st.error(f"❌ 业务逻辑层返回错误码: {res_json.get('code')} | 错误说明: {res_json.get('msg')}")
            except Exception as parse_err:
                st.error(f"❌ 解析返回失败: {parse_err}")