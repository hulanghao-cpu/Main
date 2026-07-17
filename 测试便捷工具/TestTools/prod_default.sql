SELECT event_name,sub_event_name,app_version,app_channel_id,analysis_date,app_user_id,
    CONCAT(FROM_UNIXTIME(FLOOR(os_timestamp / 1000), '%Y-%m-%d %H:%i:%s'), '.', LPAD(CAST(MOD(os_timestamp, 1000) AS CHAR), 3, '0')) AS       formatted_full_timestamp,
-- 		cast(json_extract(properties,'$._action') as string) AS action,
		cast(json_extract(properties,'$._page_name') as string) AS _page_name,
		properties
    FROM
-- 		common_event_data
-- 流水
		  public_event_data
-- 页面进入
-- 		reelshort_event_data_log
-- 		reelshort_event_data_custom
--         WHERE event_name = 'm_custom_event'
--    WHERE event_name = 'm_currency_change'
--     WHERE event_name = 'm_play_event'
--     WHERE event_name = 'm_pay_event'
     WHERE event_name = 'm_app_heart'
--     WHERE event_name = 'm_item_pv'
--     WHERE event_name = 'm_bindaccount'
--     WHERE event_name = 'm_page_enter'
--     WHERE event_name = 'm_page_exit'
--     WHERE event_name = 'm_widget_click'
--     WHERE event_name = 'subscribe_success_popup'
--            AND app_version = '2.8.00'
--            and app_version='2.1.30'
-- 				   and  sub_event_name = 'genral_notification_popup'
-- 				   and  sub_event_name = 'binding'
-- 				   and  sub_event_name = 'check_in_click'
-- 				   and  sub_event_name = 'h5_activity_vip_page'
-- 				   and  sub_event_name = 'phone_setting_page'
-- 				   and  sub_event_name = 'task_suspended_window'
-- 				   and  sub_event_name = 'm_points_currency_change'
-- 				   and  sub_event_name = 'pay_complete'
-- 				   and  sub_event_name = 'phone_activate_page'
-- 				   and  sub_event_name = 'phone_setting_page'
-- 				   and  sub_event_name = 'page_item_impression'
-- 				   and  sub_event_name = 'h5_comic_alpha_page_click'
-- 				   and  sub_event_name = 'module_click'
--             AND app_user_id = '999118790'
--         AND app_user_id IN ("999114770","999113299")
--         AND package_name IN ("com.b25drama.ios.app")
-- 				AND CAST(json_extract(properties, '$._order_src') AS STRING) = 'activity_vip_discount'
-- 				 AND CAST(json_extract(properties, '$.times') AS STRING) = '1'
-- 				and times='1'
-- 				AND app_channel_id = '1'
-- 				AND CAST(json_extract(properties, '$._page_name') AS STRING) = 'h5_activity_vip_page'
-- 				AND CAST(json_extract(properties, '$._action') AS STRING) = 'change_success'
-- 				AND CAST(json_extract(properties, '$._action') AS STRING) = 'redemption_guide_click'
-- 				AND CAST(json_extract(properties, '$._page_name') AS STRING) = 'phone_setting'
-- 				AND CAST(json_extract(properties, '$._app_account_bindtype') AS STRING) = 'phone'
-- 				AND CAST(json_extract(properties, '$._element_name') AS STRING) = 'ais_vip_icon'
-- 				AND CAST(json_extract(properties, '$._change_reason') AS STRING) = 'double_check_in_get'
-- 				AND CAST(json_extract(properties, '$.user_scene') AS STRING) != 'profile_main'
-- 				AND CAST(json_extract(properties, '$._change_reason') AS STRING) = 'vip_complete_story_task_get'
				AND analysis_date >= '2026-07-10'
     ORDER BY os_timestamp DESC
		LIMIT 50;

---- 性能埋点
--SELECT app_user_id,
--CONCAT(FROM_UNIXTIME(FLOOR(os_timestamp / 1000), '%Y-%m-%d %H:%i:%s'), '.', LPAD(CAST(MOD(os_timestamp, 1000) AS CHAR), 3, '0')) AS formatted_full_timestamp,
--properties
--FROM reelshort_perf_log
--WHERE event_name = 'm_performance_event'
--		AND os_timestamp > 1756899300000
--    AND sub_event_name = 'play_stat'
--    AND analysis_date >= '2026-07-12'
--    AND app_version >= '4.0.50'
--    AND app_user_id = ''
--    AND JSON_EXTRACT(properties, "$._action") IN ('player_start', 'player_success','player_end','player_fail','player_error')
--    ORDER BY formatted_full_timestamp DESC
--limit 50;
