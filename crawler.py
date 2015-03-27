#-*- coding: UTF-8 -*-

import os
import urllib
import urllib2
import sqlite3
import httplib
import cookielib

def try_urlopen(url):
    try:
        resp = urllib2.urlopen(url)
    except Exception, e:
        print Exception, ':', e
        resp = try_urlopen(url)

    return resp

def login():

    login_url = 'http://bbs.hackbase.com/member.php?mod=logging&action=login'
    cookiejar = cookielib.CookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookiejar))
    urllib2.install_opener(opener)

    login_response = urllib2.urlopen(login_url)
    login_source = login_response.read()

    formhash_op = login_source.find('formhash', 1, -1)
    formhash_op = login_source.find('value="', formhash_op, -1) + 7
    formhash_ed = login_source.find('"', formhash_op, -1)
    formhash = login_source[formhash_op : formhash_ed]
    print formhash

    loginhash_op = login_source.find('loginform_', formhash_ed, -1) + 10
    loginhash_ed = login_source.find('"', loginhash_op, -1)
    loginhash = login_source[loginhash_op : loginhash_ed]
    print loginhash

    seccode_op = login_source.find('seccode_', loginhash_ed, -1) + 8
    seccode_ed = login_source.find('"', seccode_op, -1)
    seccode = login_source[seccode_op : seccode_ed]
    print seccode

    values = {  
    'formhash'      : formhash,
    'referer'       : 'http://bbs.hackbase.com/forum.php',
    'username'      : 'zjvzhengs',
    'password'      : '2a28315cc1fe17dfa48ef5e6e99c987e',
    'questionid'    : 0,
    'answer'        : '',
    'seccodehash'   : seccode,
    'seccodemodid'  : 'member::logging',
    'seccodeverify' : ''
    }
    
    goal_url = 'http://bbs.hackbase.com/member.php?mod=logging&action=login&loginsubmit=yes&loginhash=' + loginhash + '&inajax=1'
    data = urllib.urlencode(values)

    req = urllib2.Request(goal_url, data)
    print req
    response = urllib2.urlopen(req)
    #response = opener.open(goal_url, data)
    print response
    the_page = response.read().decode('gbk').encode('utf8')
    #print the_page

    output = open('login.html', 'w')
    output.write(the_page)
    output.close()

    return

def cra_home():

    home_url = 'http://bbs.hackbase.com/'
    home_response = urllib2.urlopen(home_url + 'forum.php')
    home_source = home_response.read().decode('gbk').encode('utf8')

    output = open('main.html', 'w')
    output.write(home_source)
    output.close()

    forum_title_op = home_source.find('0000;">', 1, -1) + 7
    while forum_title_op - 7 != -1:
        forum_title_ed = home_source.find('<', forum_title_op, -1)
        forum_title = home_source[forum_title_op : forum_title_ed]
        print 'forum_title:' + forum_title   

        forum_url_op = home_source.find('<a href="forum.php?mod=forumdisplay&fid=', forum_title_op - 100, -1) + 9
        forum_url_ed = home_source.find('"', forum_url_op, -1)
        forum_url = home_url + home_source[forum_url_op : forum_url_ed]
        print 'forum_url:' + forum_url
        data = cra_forum(forum_url, forum_title)
        forum_title_op = home_source.find('0000;">', forum_url_ed, -1) + 7 

def cra_forum(forum_url, forum_title):
    forum_response = urllib2.urlopen(forum_url)
    forum_source = forum_response.read().decode('gbk').encode('utf8')

    if not os.path.exists(forum_title):
        os.mkdir(forum_title)
    output = open(forum_title + '/forum.html', 'w')
    output.write(forum_source)
    output.close()

    file_db = forum_title + '.db'
    conn = sqlite3.connect(file_db)
    sqlcursor = conn.cursor()

    sqlcursor.execute('''create table main_post(
    post_id         integer primany key, 
    post_title      text,
    post_view       integer,
    post_reply      integer,
    post_date       date,
    post_content    text,
    auth_id         integer,
    auth_name       text,
    auth_join_date  date,
    auth_post_num   integer,
    auth_topic_num  integer,
    auth_time       text,
    auth_level      text,
    auth_value      integer,
    auth_money      integer,
    auth_reputation integer)''')
    
    sqlcursor.execute('''create table post_detail(
    post_floor      text primany key,
    post_id         integer primany key, 
    post_date       date,
    post_content    text,
    auth_name       text,
    auth_join_date  date,
    auth_post_num   integer,
    auth_topic_num  integer,
    auth_time       text,
    auth_level      text,
    auth_value      integer,
    auth_money      integer,
    auth_reputation integer,
    auth_id         integer)''')

    post_num = 0
    post_url_op = forum_source.find('预览</a>', 1, -1)
    while post_url_op != -1:
        post_num = post_num + 1
        print post_num

        post_url_op = forum_source.find('forum.php?mod=viewthread&amp;tid=', post_url_op, -1)
        post_url_ed = forum_source.find('"', post_url_op, -1)
        post_url = 'http://bbs.hackbase.com/' + forum_source[post_url_op : post_url_ed]
        post_url = post_url.replace('&amp;', '&')
        cra_post(post_url, forum_title, sqlcursor)
        post_url_op = forum_source.find('预览</a>', post_url_ed, -1)
        print 'post_url_op' + str(post_url_op)
        print 'post_url_ed' + str(post_url_ed)
        
        conn.commit()

def cra_post(post_url, forum_title, sqlcursor):
    print 'post_url:' + post_url
    post_response = try_urlopen(post_url)
    post_source = post_response.read().decode('gbk').encode('utf8')

    post_id_op = post_url.find("tid=", 1, -1) + 4
    post_id_ed = post_url.find('&', post_id_op, -1)
    post_id = post_url[post_id_op : post_id_ed]
    print 'post_id:' + post_id

    if not os.path.exists(forum_title + '/' + post_id):
        os.mkdir(forum_title + '/' + post_id)
    output = open(forum_title + '/' + post_id + '/source.html', 'w')
    output.write(post_source)
    output.close()

    post_title_op = post_source.find('<meta name="keywords"', 1, -1)
    post_title_op = post_source.find('content="', post_title_op, -1) + 9
    post_title_ed = post_source.find('"', post_title_op, -1)
    post_title = post_source[post_title_op : post_title_ed]
    print 'post_title:' + post_title

    post_view_op = post_source.find('查看:', 1, -1)
    post_view_op = post_source.find('&nbsp;', post_view_op, -1) + 6
    post_view_ed = post_source.find('&nbsp;', post_view_op, -1)
    post_view = post_source[post_view_op : post_view_ed]
    print 'post_view:' + post_view

    post_reply_op = post_source.find('回复:', post_view_ed, -1)
    post_reply_op = post_source.find('&nbsp;', post_reply_op, -1) + 6
    post_reply_ed = post_source.find('&nbsp;', post_reply_op, -1)
    post_reply = post_source[post_reply_op : post_reply_ed]
    print 'post_reply:' + post_reply

    auth_url_op = post_source.find('<div class="authi"><a href="home.php?mod=space&amp;uid=', post_reply_ed, -1) + 28
    auth_url_ed = post_source.find('"', auth_url_op, -1)
    auth_url = 'http://bbs.hackbase.com/' + post_source[auth_url_op : auth_url_ed] + '&amp;do=profile'
    auth_url = auth_url.replace('&amp;', '&')
    print 'auth_url:' + auth_url
    auth_response = try_urlopen(auth_url)
    auth_source = auth_response.read().decode('gbk').encode('utf8')

    if not os.path.exists(forum_title):
        os.mkdir(forum_title)
    output = open(forum_title + '/auth.html', 'w')
    output.write(auth_source)
    output.close()
    
    auth_level_op = auth_source.find('用户组', 1, -1)
    auth_level_op = auth_source.find('<a href=', auth_level_op, -1)
    auth_level_op = auth_source.find('>', auth_level_op, -1) + 1
    auth_level_ed = auth_source.find('</a>', auth_level_op, -1)
    auth_level = auth_source[auth_level_op : auth_level_ed]
    print 'auth_level:' + auth_level

    auth_join_date_op = auth_source.find('注册时间</em>', auth_level_ed, -1) + 17
    auth_join_date_ed = auth_source.find(' ', auth_join_date_op, -1)
    auth_join_date = auth_source[auth_join_date_op : auth_join_date_ed]
    print 'auth_join_date:' + auth_join_date

    auth_rep_op = auth_source.find('威望</em>', auth_join_date_ed, -1) + 11
    auth_rep_ed = auth_source.find('</li>', auth_rep_op, -1)
    auth_rep = auth_source[auth_rep_op : auth_rep_ed]
    print 'auth_rep:' + auth_rep

    auth_money_op = auth_source.find('黑币</em>', auth_rep_ed, -1) + 11
    auth_money_ed = auth_source.find('</li>', auth_money_op, -1)
    auth_money = auth_source[auth_money_op : auth_money_ed]
    print 'auth_money:' + auth_money

    auth_id_op = post_source.find('uid=', auth_url_ed, -1) + 4;
    auth_id_ed = post_source.find('"', auth_id_op, -1);
    auth_id = post_source[auth_id_op : auth_id_ed]
    print 'auth_id:' + auth_id

    auth_name_op = post_source.find('>', auth_id_ed, -1) + 1
    auth_name_ed = post_source.find('</a>', auth_name_op, -1)
    auth_name = post_source[auth_name_op : auth_name_ed]
    print 'auth_name:' + auth_name

    auth_topic_num_ed = post_source.find('</a></p>主题', auth_name_ed, -1)
    auth_topic_num_op = post_source.find('">', auth_topic_num_ed - 10, -1) + 2
    auth_topic_num = post_source[auth_topic_num_op : auth_topic_num_ed]
    print 'auth_topic_num:' + auth_topic_num

    auth_post_num_ed = post_source.find('</a></p>帖子', auth_topic_num_ed, -1)
    auth_post_num_op = post_source.find('">', auth_post_num_ed - 10, -1) + 2
    auth_post_num = post_source[auth_post_num_op : auth_post_num_ed]
    print 'auth_post_num:' + auth_post_num

    auth_value_ed = post_source.find('</a></p>积分', auth_post_num_ed, -1)
    auth_value_op = post_source.find('">', auth_value_ed - 10, -1) + 2
    auth_value = post_source[auth_value_op : auth_value_ed]
    print 'auth_value:' + auth_value

    post_floor_op = post_source.find('title="您的朋友访问此链接后，您将获得相应的积分奖励"', auth_value_ed, -1)
    post_floor_op = post_source.find('<em>', post_floor_op, -1) + 4
    post_floor_ed = post_source.find('</em>', post_floor_op, -1)
    post_floor = post_source[post_floor_op : post_floor_ed]
    print 'post_floor:' + post_floor

    auth_time_op = post_source.find('<dt>累计在线</dt>', post_floor_ed, -1)
    auth_time_op = post_source.find('">', auth_time_op, -1) + 2
    auth_time_ed = post_source.find('</dd>', auth_time_op, -1)
    auth_time = post_source[auth_time_op : auth_time_ed]
    print 'auth_time:' + auth_time

    post_date_op = post_source.find('发表于 ', auth_time_ed, -1)
    post_date_op = post_source.find('20', post_date_op, -1)
    post_date_ed = post_source.find(' ', post_date_op, -1)
    post_date = post_source[post_date_op : post_date_ed]
    print 'post_date:' + post_date

    post_content_op = post_source.find('<td class="t_f"', post_date_ed, -1)
    post_content_op = post_source.find('id="', post_content_op, -1)
    post_content_op = post_source.find('">', post_content_op, -1) + 2
    post_content_ed = post_source.find('</td>', post_content_op, -1)
    post_content = post_source[post_content_op : post_content_ed]
    post_content = post_content.replace('"', '``').replace("'", "`")
    print 'post_content:' + post_content

    data = "insert into main_post (post_id, post_title, post_view, post_reply, post_date, post_content, auth_id, auth_name,auth_join_date, auth_post_num, auth_topic_num, auth_time, auth_level, auth_value, auth_money, auth_reputation) values ('" + post_id + "', '" + post_title + "', '" + post_view + "', '" + post_reply + "', '" + post_date + "', '" + post_content + "', '" + auth_id + "', '" + auth_name + "', '" + auth_join_date + "', '" + auth_post_num + "', '" + auth_topic_num + "', '" + auth_time + "', '" + auth_level + "', '" + auth_value + "', '" + auth_money + "', '" + auth_rep + "');"
#    data = data.replace('"', '`').replace("'", "`")

    sqlcursor.execute(data)
    post_floor = 1
    print 'auth_url_op:' + str(auth_url_op)
    print 'post_content_ed:' + str(post_content_ed)
    auth_url_op = post_source.find('<div class="authi"><a href="home.php?mod=space&amp;uid=', post_content_ed, -1) + 28
    print 'auth_url_op:' + str(auth_url_op)
    print 'post_floor:' + str(post_floor)

    while auth_url_op - 28 != -1:

        auth_url_ed = post_source.find('"', auth_url_op, -1)
        print 'auth_url_ed:' + str(auth_url_ed)
        auth_url = 'http://bbs.hackbase.com/' + post_source[auth_url_op : auth_url_ed] + '&amp;do=profile'
        auth_url = auth_url.replace('&amp;', '&')       
        print 'auth_url:' + auth_url
        auth_response = try_urlopen(auth_url)
        auth_source = auth_response.read().decode('gbk').encode('utf8')

        if not os.path.exists(forum_title):
            os.mkdir(forum_title)
        output = open(forum_title + '/auth.html', 'w')
        output.write(auth_source)
        output.close()

        auth_level_op = auth_source.find('用户组', 1, -1)
        auth_level_op = auth_source.find('<a href=', auth_level_op, -1)
        auth_level_op = auth_source.find('>', auth_level_op, -1) + 1
        auth_level_ed = auth_source.find('</a>', auth_level_op, -1)
        auth_level = auth_source[auth_level_op : auth_level_ed]
        print 'auth_level:' + auth_level

        auth_join_date_op = auth_source.find('注册时间</em>', auth_level_ed, -1) + 17
        auth_join_date_ed = auth_source.find(' ', auth_join_date_op, -1)
        auth_join_date = auth_source[auth_join_date_op : auth_join_date_ed]
        print 'auth_join_date:' + auth_join_date

        auth_rep_op = auth_source.find('威望</em>', auth_join_date_ed, -1) + 11
        auth_rep_ed = auth_source.find('</li>', auth_rep_op, -1)
        auth_rep = auth_source[auth_rep_op : auth_rep_ed]
        print 'auth_rep:' + auth_rep

        auth_money_op = auth_source.find('黑币</em>', auth_rep_ed, -1) + 11
        auth_money_ed = auth_source.find('</li>', auth_money_op, -1)
        auth_money = auth_source[auth_money_op : auth_money_ed]
        print 'auth_money:' + auth_money

        auth_id_op = post_source.find('uid=', auth_url_ed, -1) + 4;
        auth_id_ed = post_source.find('"', auth_id_op, -1);
        auth_id = post_source[auth_id_op : auth_id_ed]
        print 'auth_id:' + auth_id

        auth_name_op = post_source.find('>', auth_id_ed, -1) + 1
        auth_name_ed = post_source.find('</a>', auth_name_op, -1)
        auth_name = post_source[auth_name_op : auth_name_ed]
        print 'auth_name:' + auth_name

        auth_topic_num_ed = post_source.find('</a></p>主题', auth_name_ed, -1)
        auth_topic_num_op = post_source.find('">', auth_topic_num_ed - 10, -1) + 2
        auth_topic_num = post_source[auth_topic_num_op : auth_topic_num_ed]
        print 'auth_topic_num:' + auth_topic_num

        auth_post_num_ed = post_source.find('</a></p>帖子', auth_topic_num_ed, -1)
        auth_post_num_op = post_source.find('">', auth_post_num_ed - 10, -1) + 2
        auth_post_num = post_source[auth_post_num_op : auth_post_num_ed]
        print 'auth_post_num:' + auth_post_num

        auth_value_ed = post_source.find('</a></p>积分', auth_post_num_ed, -1)
        auth_value_op = post_source.find('">', auth_value_ed - 10, -1) + 2
        auth_value = post_source[auth_value_op : auth_value_ed]
        print 'auth_value:' + auth_value
     
        auth_time_op = post_source.find('<dt>累计在线</dt>', auth_value_ed, -1)
        auth_time_op = post_source.find('">', auth_time_op, -1) + 2
        auth_time_ed = post_source.find('</dd>', auth_time_op, -1)
        auth_time = post_source[auth_time_op : auth_time_ed]
        print 'auth_time:' + auth_time

        post_floor_op = post_source.find('title="您的朋友访问此链接后，您将获得相应的积分奖励"', auth_time_ed, -1)
        post_floor_op = post_source.find('<em>', post_floor_op, -1) + 4
        post_floor_ed = post_source.find('</em>', post_floor_op, -1)
        post_floor = post_source[post_floor_op : post_floor_ed]
        print 'post_floor:' + post_floor

        post_date_op = post_source.find('发表于 ', post_floor_ed, -1)
        post_date_op = post_source.find('20', post_date_op, -1)
        post_date_ed = post_source.find(' ', post_date_op, -1)
        post_date = post_source[post_date_op : post_date_ed]
        print 'post_date:' + post_date

        post_content_op = post_source.find('<td class="t_f"', post_date_ed, -1)
        post_content_op = post_source.find('id="', post_content_op, -1)
        post_content_op = post_source.find('">', post_content_op, -1) + 2
        post_content_ed = post_source.find('</td>', post_content_op, -1)
        post_content = post_source[post_content_op : post_content_ed]
        post_content = post_content.replace('"', '``').replace("'", "`")
        print 'post_content:' + post_content

        data = """insert into post_detail (post_floor, post_id, post_date, post_content, auth_name, auth_join_date, auth_post_num, auth_topic_num, auth_time, auth_level, auth_value, auth_money, auth_reputation, auth_id) values ('" + str(post_floor) + "', '" + post_id + "', '" + post_date + "', '" + post_content +  "', '" + auth_name + "', '" + auth_join_date + "', '" + auth_post_num + "', '" + auth_topic_num + "', '" + auth_time + "', '" + auth_level + "', '" + auth_value + "', '" + auth_money + "', '" + auth_rep + "', '" + auth_id + "');"""
#        data = data.replace('"', '``').reaplace("'", "`")
 
        sqlcursor.execute(data)

        print 'auth_url_op:' + str(auth_url_op)
        print 'post_content_ed:' + str(post_content_ed)
        auth_url_op = post_source.find('<div class="authi"><a href="home.php?mod=space&amp;uid=', post_content_ed, -1) + 28
        print 'auth_url_op:' + str(auth_url_op)
        print 'post_floor:' + str(post_floor)

        if auth_url_op - 28 == -1:
            next_url_op = post_source.find('下一页', 1, -1)
            print 'next_url_op:' + str(next_url_op)
            print 'auth_url_op:' + str(auth_url_op)
                   
            if next_url_op != -1:
                next_url_op = post_source.find('<a href="', next_url_op - 100, -1) + 9
                next_url_ed = post_source.find('"', next_url_op, -1)
                next_url = 'http://bbs.hackbase.com/' + post_source[next_url_op : next_url_ed]
                next_url = next_url.replace('&amp;', '&')

                post_url = next_url
                post_response = try_urlopen(post_url)
                post_source = post_response.read()

                auth_url_op = post_source.find('<div class="authi"><a href="home.php?mod=space&amp;uid=', post_content_ed, -1) + 28
          
login()
#cra_home()
cra_forum('http://bbs.hackbase.com/forum.php?mod=forumdisplay&fid=317', '网管新天地');
