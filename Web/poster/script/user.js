window.addEvent('domready', function(){
//////////////////////////////////////////////////////////////////////////
// 自定义函数区
//////////////////////////////////////////////////////////////////////////
    var toggle_log = function(text){
        var log = $('log')
        if(text){
            log.set('html', text); 
        }
        log.get('slide').slideIn().chain(function(){
            window.setTimeout(function(){
                log.slide('out');
            }, 1000);
        });
    };

    var set_tab_disabled = function(value){
        $('section_tab_button').set('disabled', value);
        $('login_tab_button').set('disabled', value);
    };

//////////////////////////////////////////////////////////////////////////
    $('log').slide('hide');

    // 如果找到 #is_action 则灌水已经开始
    if($('is_action')){
        $('section_tab_button').set('disabled', true);
    }

    // 彩蛋
    $('global_tab_button').set('disabled', true);
    window.addEvent('keypress', function(e){
        if(e.code==123){
            var global_tab_button = $('global_tab_button')
            global_tab_button.disabled = !(global_tab_button.disabled);
        }
    });

    $$('#container > .tab_button').each(function(el){
        el.store('tab_slide', new Fx.Slide(el.getNext(), {
            resetHeight: true
        }));
        el.retrieve('tab_slide').hide();
    });

    // .tab_button 事件
    $('container').addEvent('click:relay(.tab_button)', function(e, target){
        e.preventDefault();
        if(target.get('disabled')){
            return
        }
        target.getSiblings('.tab_button').each(function(el){
            el.retrieve('tab_slide').slideOut();
        });
        target.retrieve('tab_slide').toggle().chain(function(){
            window.scrollTo(0,0);
        });
    });

    // Form 里 button 事件
    $('container').addEvent('click:relay(button[name="apply"])', function(e, target){
        e.stop();
        var apply = target.get('value');
        if(apply == 'submit'){
            var form_request = target.retrieve('form_request');
            if(!form_request){
                var form = target.getParent('form');
                form_request = new Form.Request(form, $('log'), {
                    resetForm : false,
                    extraData: {
                        apply: 'submit'
                    },
                    onSuccess: function(update_el, text, xml){
                        toggle_log();
                    }
                });
                target.store('form_request', form_request);
            }
            form_request.send();
        }else if(apply == 'reset'){
            target.getParent('form').reset();
        }else if(apply == 'add'){
            var form_request = target.retrieve('form_request');
            if(!form_request){
                var form = target.getParent('form');
                var tab_page = form.getParent('.tab_page');
                form_request = new Form.Request.Append(form, tab_page);
            }
            form_request.send();
        }else if(apply == 'delete'){
            if(confirm("确认删除吗?")){
                var form_request = target.retrieve('form_request');
                if(!form_request){
                    var form = target.getParent('form');
                    form_request = new Request({
                        url: form.get('action'),
                        data: {
                            apply: 'delete'
                        },
                        onSuccess: function(text, xml){
                            toggle_log(text);
                            if(! $('log').getElement('span')){
                                target.getParent('form').destroy();
                            }
                        }
                    });
                    target.store('form_request', form_request);
                }
                form_request.send();
            }
        }else if(apply == 'login'){
            target.set('text', '正在登录...');
            target.disabled = true;
            var form_request = target.retrieve('form_request');
            if(!form_request){
                var form = target.getParent('form');
                form_request = new Form.Request(form, $('log'), {
                    resetForm : false,
                    extraData: {
                        apply: 'submit'
                    },
                    onSuccess: function(update_el, text, xml){
                        toggle_log();
                        if(! $('log').getElement('span')){
                            var table = target.getParent('table');
                            var siblings = table.getSiblings('div.auth_log');
                            table.destroy();
                            siblings.setStyle('display', 'block');
                        }else{
                            target.set('text', '登录');
                            target.disabled = false;
                        }
                    }
                });
                target.store('form_request', form_request);
            }
            form_request.send();
        }else if(apply=='action'){
            target.disabled = true;
            set_tab_disabled(true);
            target.set('text', '准备中...');
            var form_request = new Request({
                url: '/action',
                method: 'post',
                onSuccess: function(text, xml){
                    toggle_log(text);
                    target.disabled = false;
                    if($('log').getElement('span')){
                        set_tab_disabled(false);
                        target.set('text', '开始灌水');
                    }else{
                        target.set('text', '停止灌水');
                    }
                }
            });
            form_request.send();
        }

        return false;
    });

    // 登录 login_tab_button 事件
    $('login_tab_button').addEvent('click', function(){
        if(this.disabled){
            return;
        }
        if(! this.retrieve('tab_slide').open){
            var request = new Request({
                url: '/login_forms',
                method: 'post',
                onSuccess: function(text, xml){
                    $('login_forms').set('html', text);
                }
            });
            request.send();
        }
    });

    // 验证码图片事件
    $('container').addEvent('click:relay(img.login_code)', function(e, target){
        var src = target.get('src');
        target.set('src', src + new Date().getTime().toString());
    });

    // 全部登录 login_all 事件
    $('login_all').addEvent('click', function(e){
        var tab_page = e.target.getParent('div.tab_page');
        var buttons = tab_page.getElements('button.login');
        buttons.each(function(item){
            $('container').fireEvent('click', {target: item, stop: function(){}});
        });
    });
});
