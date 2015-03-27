# Crawler_Lance
Freshman_Task_Uniquestudio

内容：

黑基论坛：http://bbs.hackbase.com/

将爬取的数据存在数据库中使用sql数据库

1：主贴信息（即楼主的帖子）
	


	


表名：main_post

说明：post_id为主键

字段名
	

描述

post_id
	

帖子ID

post_title
	

帖子标题

post_view
	

帖子浏览数

post_reply
	

帖子回复数

post_date
	

发帖日期

post_content
	

帖子内容

auth_id
	

发帖人ID

auth_name
	

发帖人姓名

auth_join_date
	

发帖人注册日期

auth_post_num
	

发帖人发帖总数

auth_topic_num
	

发帖人主题总数

auth_time
	

发帖人在线时间

auth_level
	

发帖人等级

auth_value
	

发帖人积分

auth_money
	

发帖人黑币

auth_reputation
	

发帖人威望

表名：post_detail

说明：post_floor与post_id为主键

字段名
	

描述

post_floor
	

所属楼层

post_id
	

主贴ID

post_date
	

发帖日期

post_content
	

帖子内容

auth_name
	

发帖人姓名

auth_join_date
	

发帖人注册日期

auth_post_num
	

发帖人发帖总数

auth_topic_num
	

发帖人主题总数

auth_time
	

发帖人在线时间

auth_level
	

发帖人等级

auth_value
	

发帖人积分

auth_money
	

发帖人黑币

auth_reputation
	

发帖人威望

auth_id
	

发帖人ID
