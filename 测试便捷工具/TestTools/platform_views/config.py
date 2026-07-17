# 环境及凭证持久化本地路径
TOKEN_PATHS = {
    "PROD": r"E:\桌面\工程\测试便捷工具\TestTools\prod_token.txt",
    "TEST": r"E:\桌面\工程\测试便捷工具\TestTools\temptoken.txt"
}

# 核心业务时区规范
TIMEZONES = {
    "CN": "Asia/Shanghai",
    "LA": "America/Los_Angeles"
}

# 🔥【全量防御式初始化】：确保所有读写过的 key 100% 在这里注册闭环，防止任何 KeyError
INIT_SESSION_STATES = {
    "search_uid": "",
    "test_token": "",
    "prod_token": "",
    "is_prod": False,
    "menu_selection": "👤 账号运维管理",

    # 🗄️ 数据库相关状态锁
    "cache_db_query_res": None,
    "db_connect_error": None,
    "db_connection_handle": None,
    "custom_sql_input": "",

    # 📄 效率工具箱状态锁
    "tab7_json_output_cache": None,
    "cache_ts_to_date_res": "",
    "cache_date_to_ts_res": "",
    "tab1_ip_textarea": "",

    # 👤 完美对齐 deleteUser.py 的原始页面级业务缓存锁
    "tab1_inspect_data": None,  # 🟢【就是这里！】确保这个键被完美初始化
    "cache_tab1_user_info": None,
    "cache_tab1_ip_res": None,
    "cache_tab1_wl_res": None,
    "cache_tab1_lookup_res": None,
    "cache_tab1_reset_res": None,

    # 👑 会员、福利、上报及认证助手缓存锁
    "cache_tab2_vip_res": None,
    "cache_tab2_coin_res": None,
    "cache_tab3_welfare_res": None,
    "cache_tab5_report_res": None,
    "tab3_login_success_data": None,

# 🚀【新增压测功能状态锁】
    "cache_stress_test_report": None,   # 存放压测完的 DataFrame 报告
    "cache_stress_test_summary": None,  # 存放压测完的聚合统计指标
    "stress_editor_version": 0          # 压测输入框的版本计数器
}