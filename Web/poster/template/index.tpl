<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">

<html xmlns="http://www.w3.org/1999/xhtml">
<head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
    <link rel="stylesheet" type="text/css" href="css/screen.css" />
    <link rel="stylesheet" type="text/css" href="css/plugins/buttons/screen.css" />
    <link rel="stylesheet" type="text/css" href="css/ie.css" />
    <link rel="stylesheet" type="text/css" href="css/user.css" />
    <script type="text/javascript" src="script/mootools.js"></script>
    <script type="text/javascript" src="script/mootools-more.js"></script>
    <script type="text/javascript" src="script/user.js"></script>
    <title>灌水无罪:P</title>
</head>
<body>
<div id="log"></div>
<div class="container">
    <div id="container" class="span-12 prepend-6 append-6 lass">
        <div id="global_tab_button" class="tab_button">Global</div>
        <div class="tab_page">
            %include global_form **global_configs
        </div>
        <div id="section_tab_button" class="tab_button">配置</div>
        <div class="tab_page">
            <form action="/add/user_section" method="post">
                <button class="add" name="apply" value="add" style="margin-left: 10px;">新增Section</button>
            </form>
            <hr/>
            %for section_name in user_sections:
            %include section_form section_name=section_name, **user_sections[section_name]
            %end
        </div>
        <div id="login_tab_button" class="tab_button">登录</div>
        <div class="tab_page">
            <button id="login_all" class="login_all" style="margin-left: 10px;">全部登录</button>
            <hr/>
            <div id="login_forms">正在读取帐户信息...</div>
        </div>
    </div>
</div>
%if is_action:
<div id="is_action" style="display:none;"></div>
%end
</body>
</html>
