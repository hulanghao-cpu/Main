import streamlit as st
import requests

def render_playback_view():
    st.subheader("📊 视频/作品播放时长数据上报（仅测试服支持）")
    col1, col2 = st.columns(2)
    with col1:
        report_uid = st.text_input("用户 UID (uid):", value=st.session_state.search_uid, key="report_uid_in")
        play_seconds = st.number_input("上报播放秒数 (play_seconds):", value=30, min_value=0, step=5, key="report_seconds_in")
        seq_id = st.number_input("序列 ID (seq_id):", value=1, min_value=0, step=1, key="report_seq_in")
    with col2:
        book_id = st.text_input("作品书籍 ID (book_id):", value="6a0fcf4e6aabcff0c805105a", key="report_book_in")
        chapter_id = st.text_input("目标章节 ID (chapter_id):", value="tv8ibgwzr0", key="report_chapter_in")

    if st.button("🚀 立即上报播放时长", type="primary", key="report_submit_btn"):
        if not report_uid: st.error("❌ 用户 UID 不能为空！")
        else:
            with st.spinner("上报中..."):
                r_headers = {
                    "channelId": "AVG20001", "uid": str(report_uid), "clientVer": "4.0.00", "Accept": "*/*",
                    "session": "9c3de312d33e6efe99ac52407f89d731", "apiVersion": "1.4.19", "devId": "68DCDBAA-8153-45C8-9B93-B0BB45589161",
                    "User-Agent": "ReelShort/4.0.00", "lang": "en", "ts": "1783341250", "sign": "c08a778dff26d2e67b7135e85f28adadfe4548b520f09980e08655f2836d23a6"
                }
                try:
                    response = requests.post(url="https://dev-project-v-api.stardustworld.cn/api/video/user/reportPlaybackDuration?secret=2024062716138845",
                                             headers=r_headers, data={"book_id": str(book_id), "chapter_id": str(chapter_id), "play_seconds": str(play_seconds), "seq_id": str(seq_id)}, timeout=15)
                    st.session_state["cache_tab5_report_res"] = {"code": response.status_code, "text": response.text}
                except Exception as e: st.error(f"异常: {e}")

    if st.session_state["cache_tab5_report_res"] is not None:
        rep_res = st.session_state["cache_tab5_report_res"]
        st.markdown("### 📥 播放时长接口上报结果 center")
        st.code(f"状态码: {rep_res['code']}\n返回内容: {rep_res['text']}")
        if rep_res['code'] == 200: st.success("🎉 数据流上报成功，已持久化锁屏！")