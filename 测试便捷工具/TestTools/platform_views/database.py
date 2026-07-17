import pymysql
import streamlit as st
from pymysql.cursors import DictCursor


@st.cache_resource
def init_db_connection():
    """
    建立与阿里云 RDS 数据库的底层安全长连接（带 10秒超时控制）
    """
    db_config = {
        "host": "amv-2ev8c441hro07g58800000101o.ads.aliyuncs.com",
        "port": 3306,
        "user": "test_r01",
        "password": "test_r01123%",
        "database": "chapters_log",
        "charset": "utf8mb4",
        "cursorclass": DictCursor,
        "connect_timeout": 10
    }
    try:
        connection = pymysql.connect(**db_config)
        st.session_state["db_connect_error"] = None  # 清空错误日志
        return connection
    except Exception as e:
        st.session_state["db_connect_error"] = str(e)
        st.cache_resource.clear()  # 触发失败时必须重置缓存锁
        return None

def run_db_query(sql, params=None):
    """
    通用 SQL 高效查询包装器（支持全量延迟按需加载调用）
    """
    if st.session_state["db_connection_handle"] is None:
        st.session_state["db_connection_handle"] = init_db_connection()
        if st.session_state["db_connection_handle"] is None:
            return ["数据库未连接"]

    conn = st.session_state["db_connection_handle"]
    try:
        # 执行前主动进行 TCP 网络活性探针校验，防止阿里云主动切线
        conn.ping(reconnect=True)
        with conn.cursor() as cursor:
            cursor.execute(sql, params)
            return cursor.fetchall()
    except Exception as db_err:
        st.session_state["db_connect_error"] = str(db_err)
        st.cache_resource.clear()
        st.session_state["db_connection_handle"] = None  # 断线安全熔断
        return None