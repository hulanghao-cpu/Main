import warnings
# 强行过滤掉 cryptography 库抛出的所有弃用警告，防止刷爆控制台导致网络断开
warnings.filterwarnings("ignore", category=UserWarning, module="cryptography")
warnings.filterwarnings("ignore", message=".*Python 3.8 is no longer supported.*")

import sys
import os

# 🚀【绝对项目根目录强制锁定中间件】
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

import streamlit as st
import time
from datetime import datetime
import pytz

# 1. 网页基础配置
st.set_page_config(page_title="测试自动化工具接口运维平台", layout="wide")

# 2. 挂载顶级时钟占位空槽位
clock_placeholder = st.empty()

# 3. 🚨【状态机循环注入中间件】：将 config 里的初始值锁进状态机
from config import INIT_SESSION_STATES, TIMEZONES, TOKEN_PATHS

for state_key, default_val in INIT_SESSION_STATES.items():
    if state_key not in st.session_state:
        st.session_state[state_key] = default_val

# 4. 左侧侧边栏布局
with st.sidebar:
    st.header("🌐 环境选择")
    env_selection = st.radio("当前操作环境：", ["🧪 测试环境 (Test)", "🔥 正式环境 (Prod)"], key="global_env_select")
    st.session_state.is_prod = "正式" in env_selection
    is_prod = st.session_state.is_prod

    st.header("🎯 功能导航菜单")
    # 🟢 🔥【完全同步修复】：确保列表里 100% 包含我们新加的压测机菜单，位置可以随意放置
    menu_selection = st.radio(
        "请选择要操作的功能：",
        [
            "👤 账号运维管理",
            "👑 会员权限管理",
            "🎁 福利页配置查询",
            "📊 播放时长上报",
            "🛠️ 研发效率工具箱",
            "⚡ 接口并发压测机",  # 👈 确保这一行在列表中安全挂载
            "🔑 登录认证助手"
        ],
        key="main_menu_radio_widget"  # 显式指定组件key防止冲突
    )
    st.session_state.menu_selection = menu_selection
    st.markdown("---")
    st.header("🔑 凭证配置")
    token_file = TOKEN_PATHS["PROD"] if is_prod else TOKEN_PATHS["TEST"]
    token_state_key = "prod_token" if is_prod else "test_token"
    token_source = st.radio(f"[{env_selection}] Token 来源：", [f"从 {token_file} 读取", "手动输入凭证"],
                            key="sidebar_token_src")

    if token_source.startswith("从"):
        if os.path.exists(token_file):
            try:
                with open(token_file, "r", encoding="utf-8") as f:
                    st.session_state[token_state_key] = f.read().strip()
                st.success(f"✅ 已载入{env_selection}凭证")
            except Exception:
                pass
        else:
            st.error(f"❌ 未找到 {token_file} 文件")
    else:
        st.session_state[token_state_key] = st.text_input("请输入完整 Token (含 Bearer):",
                                                          value=st.session_state.get(token_state_key, ""),
                                                          key="sidebar_token_input_field")

    current_token = st.session_state.get(token_state_key, "")
    if current_token: st.caption(f"当前生效 Token: `{current_token[:25]}...`")

# 5. 推流渲染顶部纯黑居中、高科技感时区时钟大盘看板
tz_beijing = pytz.timezone(TIMEZONES["CN"])
tz_los_angeles = pytz.timezone(TIMEZONES["LA"])
now_u = datetime.fromtimestamp(time.time(), pytz.utc)
t_bj = now_u.astimezone(tz_beijing).strftime("%H:%M:%S")
t_la = now_u.astimezone(tz_los_angeles).strftime("%H:%M:%S")

# 使用 Container 包装，实现 HTML 大盘和 Streamlit 按钮的组件融合
with clock_placeholder.container():
    # 顶部黑底大盘 (包含标题、时钟)
    st.markdown(
        f"""
        <div style="background-color: #121212; padding: 15px 20px; border-radius: 6px 0px 0px 6px; box-shadow: 0 4px 6px rgba(0,0,0,0.15); display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 15px;">
            <div style="font-size: 22px; font-weight: bold; color: #ffffff; letter-spacing: 1px; margin: 0;">
                🚀 接口自动化运维与测试平台 MRNTPT
            </div>
            <div style="display: flex; justify-content: center; align-items: center; gap: 20px;">
                <div style="background-color: #1e1e1e; border-left: 4px solid #ff922b; padding: 6px 15px; border-radius: 4px; min-width: 140px;">
                    <div style="font-size: 11px; color: #adb5bd; font-weight: bold;">🇨🇳 北京时间 (CN)</div>
                    <div style="font-size: 16px; color: #ff922b; font-family: monospace; font-weight: bold;">{t_bj}</div>
                </div>
                <div style="background-color: #1e1e1e; border-left: 4px solid #339af0; padding: 6px 15px; border-radius: 4px; min-width: 140px;">
                    <div style="font-size: 11px; color: #adb5bd; font-weight: bold;">🇺🇸 洛杉矶时间 (LA)</div>
                    <div style="font-size: 16px; color: #339af0; font-family: monospace; font-weight: bold;">{t_la}</div>
                </div>
                <div style="background-color: #1e1e1e; border-left: 4px solid #22b8cf; padding: 6px 15px; border-radius: 4px; min-width: 140px;">
                    <div style="font-size: 11px; color: #adb5bd; font-weight: bold;">⏳ Unix 时间戳</div>
                    <div style="font-size: 16px; color: #22b8cf; font-family: monospace; font-weight: bold;">{int(time.time())}</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # 利用 Streamlit 的列布局，在标题栏下方提供精美的一键展开/复制工具栏
    col_cmd_l, col_cmd_r = st.columns([8.5, 1.5])
    with col_cmd_r:
        show_cmd = st.toggle("📋 查看 Bundletool 命令", value=False)

    if show_cmd:
        st.info("💡 点击右侧按钮可直接一键复制命令：")
        st.code("java -jar bundletool-all-1.11.0.jar install-apks --apks=", language="bash")

# 刷新大盘数据行
col_refresh_l, col_refresh_r = st.columns([8.5, 1.5])
with col_refresh_r:
    if st.button("🔄 刷新全盘数据/时间戳", type="secondary", use_container_width=True):
        st.rerun()

# 6. 大盘顶级分发路由器分流控制（采用最新的 st.query_params 标准兼容升级）
if menu_selection == "👤 账号运维管理":
    from v1_account import render_account_view

    render_account_view()
elif menu_selection == "👑 会员权限管理":
    from v2_vip import render_vip_view

    render_vip_view()
elif menu_selection == "🎁 福利页配置查询":
    from v3_welfare import render_welfare_view

    render_welfare_view()
elif menu_selection == "📊 播放时长上报":
    from v5_playback import render_playback_view

    render_playback_view()
elif menu_selection == "🔑 登录认证助手":
    from v6_auth import render_auth_view

    render_auth_view()
elif menu_selection == "🛠️ 研发效率工具箱":
    from v7_efficiency import render_efficiency_view

    render_efficiency_view()

    # app.py 路由分发区追加：
elif menu_selection == "⚡ 接口并发压测机":
    from v8_stress import render_stress_view

    render_stress_view()

