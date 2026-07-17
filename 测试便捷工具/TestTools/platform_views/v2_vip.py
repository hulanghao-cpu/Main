import streamlit as st
import requests


def render_vip_view():
    env_selection = "🔥 正式环境 (Prod)" if st.session_state.is_prod else "🧪 测试环境 (Test)"
    st.subheader(f"👑 [{env_selection}] 用户权限与货币资产变更")
    is_prod = st.session_state.is_prod
    current_token = st.session_state.prod_token if is_prod else st.session_state.test_token
    pub_url = "https://v-adm.crazymaplestudios.com" if is_prod else "https://test-v-adm.stardustworld.cn"

    common_headers = {
        "Authorization": str(current_token), "appid": "cm1009", "Accept": "*/*",
        "Accept-Language": "zh-CN,zh;q=0.9", "cache-control": "no-cache", "pragma": "no-cache",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    if not is_prod:
        tab_vip, tab_currency = st.tabs(["📆 VIP 天数补发/变更", "💰 金币/金券/积分加减"])
    else:
        tab_vip = st.container()

    with tab_vip:
        st.markdown("### 📱 选择目标用户与数据核对")
        vip_device_source = st.radio("UID 获取方式：",
                                     ["自动联动当前查询结果", "选择已有设备查询并校验", "手动输入 UID"],
                                     horizontal=True, key="tab2_uid_source")
        if "tab2_vip_uid_dev_result" not in st.session_state: st.session_state["tab2_vip_uid_dev_result"] = ""
        vip_uid = ""
        user_vip_verified = None

        if vip_device_source == "自动联动当前查询结果":
            vip_uid = st.session_state.search_uid
            st.text_input("当前联动到的 UID:", value=vip_uid, key="tab2_vip_uid_linked", disabled=True)
        elif vip_device_source == "选择已有设备查询并校验":
            vip_device_options = {"设备 (SM-F731U1)": "c29dbebf292b9aa4"} if is_prod else {
                "Android 测试机 (c29d...)": "c29dbebf292b9aa4",
                "iOS 测试机 (68DC...)": "68DCDBAA-8153-45C8-9B93-B0BB45589161"}
            selected_vip_dev_label = st.selectbox("选择目标测试设备：", list(vip_device_options.keys()),
                                                  key="tab2_vip_device_select")
            vip_dev_id = vip_device_options[selected_vip_dev_label]

            if st.button("🔍 获取该设备当前的 UID 并校验", key="tab2_get_uid_btn"):
                if not current_token:
                    st.error("请先在左侧侧边栏配置 Token！")
                else:
                    with st.spinner("正在获取 UID..."):
                        params = {"uid": "", "dev_model": f"{vip_dev_id}\t", "page": 1, "page_size": 20,
                                  "secret": "2024062716138845"} if is_prod else {"sid": 0, "dev_id": str(vip_dev_id),
                                                                                 "ustatus": 0, "uname": "Guest"}
                        try:
                            res = requests.get(f"{pub_url}/api/member", headers=common_headers, params=params,
                                               timeout=10)
                            if res.status_code == 200:
                                collections = res.json().get("data", {}).get("collections", [])
                                if collections:
                                    user_vip_verified = collections[0]
                                    st.session_state.search_uid = str(user_vip_verified.get("uid"))
                                    st.session_state["tab2_vip_uid_dev_result"] = st.session_state.search_uid
                                    st.success("🎯 成功获取并自动同步校验数据！")
                                    st.rerun()
                                else:
                                    st.warning("⚠️ 该设备未绑定 any 账号")
                            else:
                                st.error(f"接口请求失败: {res.status_code}")
                        except Exception as e:
                            st.error(f"查询异常: {e}")
            vip_uid = st.text_input("解析出的用户 UID:", key="tab2_vip_uid_dev_result")
        else:
            vip_uid = st.text_input("请输入目标用户 UID:", key="tab2_vip_uid_manual")

        if st.button("🔍 强制校验该手动输入的 UID 信息", key="tab2_manual_verify_btn"):
            if vip_uid:
                params = {"uid": str(vip_uid), "page": 1, "page_size": 20}
                if is_prod: params["secret"] = "2024062716138845"
                res = requests.get(f"{pub_url}/api/member", headers=common_headers, params=params, timeout=10)
                collections = res.json().get("data", {}).get("collections", [])
                if collections: user_vip_verified = collections[0]

        if user_vip_verified: st.info(f"📋 充值前数据核对 -> 渠道 ID: `{user_vip_verified.get('channel_id', '未知')}`")

        st.markdown("---")
        st.markdown("### ⚙️ 变更参数配置")
        opt_mapping = {"➕ 增加会员天数 (充值)": 0, "➖ 减少会员天数 (扣除)": 1}
        opt_label = st.radio("操作类型 (opt):", options=list(opt_mapping.keys()), horizontal=True, key="tab2_opt_radio")
        opt_type = opt_mapping[opt_label]

        col1, col2 = st.columns(2)
        with col1:
            vip_days = st.number_input(f"请设定要天数 (days):", value=1, min_value=1, step=1, key="tab2_days_input")
        with col2:
            paid_category = st.number_input("付费类别 (paid_category):", value=2, step=1, key="tab2_category_input")

        if st.button(f"🚀 确认提交权限变更 center", type="primary" if opt_type == 0 else "secondary",
                     key="tab2_submit_btn"):
            if not current_token:
                st.error("请先配置 Token！")
            elif not vip_uid:
                st.error("❌ UID 不能为空！")
            else:
                with st.spinner("正在提交请求..."):
                    try:
                        response = requests.post(url=f"{pub_url}/api/member/add-vip",
                                                 headers={"Authorization": str(current_token), "appid": "cm1009",
                                                          "Content-Type": "application/json;charset=UTF-8"},
                                                 json={"opt": int(opt_type), "paid_category": int(paid_category),
                                                       "uid": int(vip_uid) if str(vip_uid).isdigit() else vip_uid,
                                                       "days": int(vip_days)}, timeout=15)
                        st.session_state["cache_tab2_vip_res"] = {"code": response.status_code, "text": response.text}
                    except Exception as e:
                        st.error(f"异常: {e}")

        if st.session_state["cache_tab2_vip_res"] is not None:
            vip_res = st.session_state["cache_tab2_vip_res"]
            st.markdown("### 📥 VIP变更接口返回结果")
            st.code(f"状态码: {vip_res['code']}\n返回内容: {vip_res['text']}")
            if vip_res['code'] == 200: st.success("🎉 VIP 权限资产调整成功下发！")

    if not is_prod:
        with tab_currency:
            st.markdown("### 💰 用户金币、金券、会员积分资产变更管理")
            coin_target_uid = st.text_input("目标操作用户 UID:", value=st.session_state.search_uid, key="tab2_coin_uid")
            coin_opt_label = st.radio("变更动作类型 (opt):", ["➕ 添加用户资产", "➖ 扣除/减少用户资产"], horizontal=True,
                                      key="tab2_coin_opt")
            coin_opt = 0 if "添加" in coin_opt_label else 1

            st.markdown("#### ⚙️ 选择需要调整的货币类别及数量")
            col_c1, col_c2, col_c3 = st.columns(3)
            with col_c1:
                chk_coins = st.checkbox("🪙 金币 (coins)", value=True, key="chk_coins")
                val_coins = st.number_input("金币数量:", value=100, min_value=1, step=10, key="val_coins",
                                            disabled=not chk_coins)
            with col_c2:
                chk_bonus = st.checkbox("🎟️ 金券 (bonus)", value=True, key="chk_bonus")
                val_bonus = st.number_input("金券数量:", value=10, min_value=1, step=5, key="val_bonus",
                                            disabled=not chk_bonus)
            with col_c3:
                chk_points = st.checkbox("⭐ 会员积分 (vip_points)", value=False, key="chk_points")
                val_points = st.number_input("积分数量:", value=50, min_value=1, step=10, key="val_points",
                                             disabled=not chk_points)

            st.markdown("---")
            coin_btn_word = "执行资产添加" if coin_opt == 0 else "执行资产扣除"

            if st.button(f"🚀 确认{coin_btn_word}", type="primary" if coin_opt == 0 else "secondary",
                         key="tab2_coin_submit_btn"):
                if not current_token:
                    st.error("请先在左侧侧边栏配置当前环境的 Token！")
                elif not coin_target_uid:
                    st.error("❌ 操作用户的 UID 不能为空！")
                elif not (chk_coins or chk_bonus or chk_points):
                    st.warning("⚠️ 请至少勾选一种需要变更的货币类别！")
                else:
                    with st.spinner("正在向测试网关提交资产变更请求..."):
                        coin_url = "https://test-v-adm.stardustworld.cn/api/member/add-coin"
                        coin_headers = {
                            "Accept": "application/json", "Accept-Language": "zh-CN,zh;q=0.9",
                            "Cache-Control": "no-cache",
                            "Content-Type": "application/json;charset=UTF-8",
                            "Origin": "https://test-v-adm.stardustworld.cn",
                            "User-Agent": "Mozilla/5.0", "appId": "cm1009", "authorization": str(current_token).strip()
                        }
                        coin_payload = {"opt": int(coin_opt), "uid": int(coin_target_uid) if str(
                            coin_target_uid).isdigit() else coin_target_uid}
                        if chk_coins: coin_payload["coins"] = int(val_coins)
                        if chk_bonus: coin_payload["bonus"] = int(val_bonus)
                        if chk_points: coin_payload["vip_points"] = int(val_points)

                        try:
                            response = requests.post(url=coin_url, headers=coin_headers, json=coin_payload, timeout=15)
                            st.session_state["cache_tab2_coin_res"] = {"code": response.status_code,
                                                                       "text": response.text}
                        except Exception as e:
                            st.error(f"❌ 货币变动网络异常: {e}")

            if st.session_state["cache_tab2_coin_res"] is not None:
                coin_res = st.session_state["cache_tab2_coin_res"]
                st.markdown("### 📥 货币接口返回结果 center")
                st.code(f"状态码: {coin_res['code']}\n返回内容: {coin_res['text']}")
                if coin_res['code'] == 200: st.success("🎉 账户资产变更成功！")