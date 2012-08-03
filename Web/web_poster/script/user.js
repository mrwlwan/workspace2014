dojo.require('dojo.data.ItemFileReadStore');

dojo.require('dijit.layout.BorderContainer');
dojo.require('dijit.layout.TabContainer');
dojo.require('dijit.layout.StackContainer');
dojo.require('dijit.layout.StackController');
dojo.require('dijit.layout.AccordionContainer');
dojo.require('dijit.layout.ContentPane');

dojo.require('dijit.form.Form');
dojo.require('dijit.form.Button');
dojo.require('dijit.form.ComboBox');
dojo.require('dijit.form.Select');
dojo.require('dijit.form.CheckBox');
dojo.require('dijit.form.SimpleTextarea');
dojo.require('dijit.form.TextBox');

//////////////////////////////////////////////////////////////////
var saved_forms = ['get_form', 'general_form'];
var saved_text_inputs = ['get_data', 'get_code_image_url', 'get_code_key', 'get_code'];
var saved_check_inputs = ['get_is_has_code'];

//////////////////////////////////////////////////////////////////
// 取得object value,如果没有相应的key,则返回一个默认值.
function get_value(obj, key, default_value){
    if(key in obj){
        return obj[key];
    }
    return default_value;
}

// 普通的 form 提交 subscribe
dojo.subscribe('form_submit', function(form, e){
    e.preventDefault();
    show_process_message('处理中...');
    dojo.xhrPost({
        form: form,
        load: function(response){
            show_content_message(response);
        }
    });
});

// 简单的 xhr 提交
function simple_xhr(url){
    return function(){
        show_process_message('处理中...');
        dojo.xhrPost({
            'url': url,
            method: 'POST',
            load: function(response){
                show_content_message(response);
            }
        });
    };
}

// 消息输出到 #content 函数
function show_content_message(msg){
    var content = dijit.byId('content');
    var is_keep = dijit.byId('is_content_keep').checked;
    var is_scroll = dijit.byId('is_content_scroll').checked;
    if(is_keep){
        msg = content.get('value') + '\n' + msg;
    }
    content.set('value', msg);
    if(is_scroll){
        content.domNode.scrollTop = content.domNode.scrollHeight;
    }
}

// 显示准备中的信息. 
function show_process_message(msg){
    if(!dijit.byId('is_content_keep').checked){
        var content = dijit.byId('content');
        content.set('value', msg);
    }
}


// 取得需要保存进会话的 datas.
function get_session_data(){
    var data = {}
    saved_forms.forEach(function(form_id){
        data = dojo.mixin(data, dijit.byId(form_id).get('value'));
    });
    saved_text_inputs.forEach(function(input_id){
        var input = dijit.byId(input_id);
        data[input.get('name')] = input.get('value');
    });
    saved_check_inputs.forEach(function(input_id){
        var input = dijit.byId(input_id);
        var input_value = input.get('value');
        // 将 false 值变为0; true 值变为1
        data[input.get('name')] =  input_value ? 1 : 0; 
    });
    return data
}

// 更新当前Session
function update_session_data(data){
    saved_forms.forEach(function(form_id){
        var form = dijit.byId(form_id);
        var form_data = form.get('value');
        var value = {}
        for(var name in form_data){
            value[name] = get_value(data, name, '');
        }
        form.set('value', value);
    });
    saved_text_inputs.forEach(function(input_id){
        var input = dijit.byId(input_id);
        var name = input.get('name');
        input.set('value', get_value(data, name, ''));
    });
    saved_check_inputs.forEach(function(input_id){
        var input = dijit.byId(input_id);
        var name = input.get('name');
        input.set('value', parseInt(get_value(data, name, 0)));
    });
}

//////////////////////////////////////////////////////////////////
// 正则测试 form 的 Enter 按键提交
function re_test_form_enter(e){
    if(e.keyCode == 13){
        dojo.publish('form_submit', [dojo.byId('re_test_form'), e]);
    }
}

// Search form 的 Enter 按键提交
function search_form_enter(e){
    if(e.keyCode == 13){
        dojo.publish('form_submit', [dojo.byId('search_form'), e]);
    }
}

// 清除 #content 的消息函数
function clear_content_message(){
    dijit.byId('content').set('value', '');
}

// 保存 #content 的消息事件
function save_content_message(){
    dojo.xhrPost({
        'url': '/save_log',
        method: 'POST',
        content: {'content': dijit.byId('content').get('value')},
        load: function(response){
            show_content_message(response);
        }
    });
}



// 正则测试, 是否应用网页抓取的文本.是的话, 将 re_test_text 文本域禁用.
function re_test_use_fetch_content(new_value){
    var re_test_text = dijit.byId('re_test_text')
    re_test_text.set('disabled', new_value);
}

// 搜索, 是否应用网页抓取的文本.是的话, 将 search_text 文本域禁用.
function search_use_fetch_content(new_value){
    var search_text = dijit.byId('search_text');
    search_text.set('disabled', new_value);
}

// 是否需要验证码图片, 否则将验证码下的几个 weidget 禁用.
function is_has_code(new_value){
    var method = dijit.byId('get_method').get('value').toLowerCase().trim();
    var value = true;
    if(method == 'post'){
        value = !new_value;
    }
    dijit.byId('get_code_image_url').set('disabled', value);
    dijit.byId('get_code_image_bn').set('disabled', value);
    dijit.byId('get_code_key').set('disabled', value);
    dijit.byId('get_code').set('disabled', value);
}

// 提交方法改变时的事件
function is_change_method(new_value){
    var value = new_value.toLowerCase().trim() == 'get' ? true : false;
    var is_has_code_checkbox = dijit.byId('get_is_has_code');
    var is_has_code_checkbox_value = is_has_code_checkbox.get('value');
    dijit.byId('get_data').set('disabled',value);
    is_has_code_checkbox.set('disabled', value);
    if(is_has_code_checkbox_value){
        is_has_code(!value);
    }
}

// 获取验证码图片
function refresh_code_image(){
    var url = dijit.byId('get_code_image_url').get('value').trim();
    var image = dojo.byId('get_code_image');
    dojo.attr(image, 'src', '/get_code_image?url=' + url + '&time=' + new Date().getTime().toString());
    dojo.style(image, 'display', 'inline');
}

function save_session(){
    var session_select = dijit.byId('session_session');
    var session_name = session_select.get('value').trim();
    if(!session_name){
        alert('Session名称不能为空!');
        return
    }
    var data = get_session_data();
    data['session_name'] = session_name
    dojo.xhrPost({
        url: '/session/save',
        method: 'POST',
        content: data,
        load: function(response){
            show_content_message(response);
            if(response.search('成功')>=0){
                session_json.close();
            }
        }
    });
}

function load_session(){
    var session_select = dijit.byId('session_session');
    var session_name = session_select.get('value').trim();
    if(!session_name){
        alert('请选择要删除的 Session!');
        return
    }
    dojo.xhrPost({
        url: '/session/load',
        method: 'POST',
        content: {'session_name': session_name},
        handleAs: 'json',
        load: function(response){
            try{
                update_session_data(response);
                show_content_message('加载 Session: ' + session_name + ' 成功!');
            }catch(e){
                show_content_message('加载 Session: ' + session_name + ' 失败!');
            }
        }
    });
}

function remove_session(){
    var session_select = dijit.byId('session_session');
    var session_name = session_select.get('value').trim();
    if(!session_name){
        alert('请选择要删除的 Session!');
        return
    }
    if(!confirm('确定删除 Session: ' + session_name + ' 吗?')){
        return
    }
    dojo.xhrPost({
        url: '/session/remove',
        method: 'POST',
        content: {'session_name': session_name},
        load: function(response){
            show_content_message(response);
            if(response.search('成功')>=0){
                session_json.close();
                session_select.set('displayedValue', '');
            }
        }
    });
}

function clear_session(){
    if(!confirm('确定清空所有 Sessions 吗?')){
        return
    }
    dojo.xhrPost({
        url: '/session/clear',
        method: 'POST',
        load: function(response){
            show_content_message(response);
            if(response.search('成功')>=0){
                session_json.close();
                dijit.byId('session_session').set('displayedValue', '');
            }
        }
    });
}


//////////////////////////////////////////////////////////////////
//dojo.ready(function(){
    //// 左侧栏点击事件, 设置top_panel
    //var bn = dijit.byId('stack_controller');
    //dojo.connect(bn, 'onButtonClick', function(e, page){
        //var top_panel = dijit.byId('top_panel');
        //top_panel.set('content', e.title);
        //dijit.byId('app_layout').layout();
    //});
//});
