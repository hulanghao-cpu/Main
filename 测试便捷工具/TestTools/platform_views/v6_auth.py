import streamlit as st
import requests
from config import TOKEN_PATHS


def render_auth_view():
    env_selection = "🔥 正式环境 (Prod)" if st.session_state.is_prod else "🧪 测试环境 (Test)"
    st.subheader(f"🔑 快捷登录及 Token 刷新 ({env_selection})")

    token_file = TOKEN_PATHS["PROD"] if st.session_state.is_prod else TOKEN_PATHS["TEST"]
    token_state_key = "prod_token" if st.session_state.is_prod else "test_token"

    input_user = st.text_input("登录用户名:", value="hulanghao@crazymaplestudio.com", key="tab3_username")
    input_pass = st.text_input("登录密码:", value="hlh1564325769", type="password", key="tab3_password")

    if st.button("⚡ 一键登录并校验激活 Token", type="primary", key="tab3_login_btn"):
        with st.spinner(f"正在建立与 {env_selection} 的最高权限认证流..."):
            base_auth_url = "https://amc.crazymaplestudios.com" if st.session_state.is_prod else "https://amc-test.crazymaplestudios.com"
            login_url = f"{base_auth_url}/api/login"
            login_headers = {"accept": "application/json", "content-type": "application/json;charset=UTF-8"}
            login_payload = {"username": str(input_user).strip(), "password": str(input_pass).strip()}
            if not st.session_state.is_prod:
                login_payload.update(
                    {"system_id": "19", "jump_url": "https://test-v-adm.stardustworld.cn/resource-manage/story-list"})

            try:
                login_res = requests.post(url=login_url, headers=login_headers, json=login_payload, timeout=10)
                if login_res.status_code == 200:
                    res_json = login_res.json()
                    if res_json.get("code") in [0, 200]:
                        bearer_token = f"Bearer {res_json['data']['access_token']}"
                        st.session_state[token_state_key] = bearer_token
                        with open(token_file, "w", encoding="utf-8") as f: f.write(bearer_token)
                        st.session_state["tab3_login_success_data"] = {"token": bearer_token,
                                                                       "user_info": res_json["data"]}
                        st.toast("凭证已同步，切换功能菜单即可直接使用！", icon="🚀")
                        st.rerun()
                else:
                    st.error(f"❌ HTTP 状态码: {login_res.status_code}")
            except Exception as e:
                st.error(f"❌ 运行异常: {e}")

    if st.session_state["tab3_login_success_data"] is not None:
        data_cache = st.session_state["tab3_login_success_data"]
        st.markdown("---")
        st.success(f"🎉 {env_selection} 登录流全线激活！")
        col_l, col_r = st.columns(2)
        with col_l:
            st.code(data_cache["token"])
        with col_r:
            st.json(data_cache["user_info"])
        if st.button("🗑️ 清除当前登录展示面板", key="tab3_clear_view_btn"):
            st.session_state["tab3_login_success_data"] = None
            st.rerun()