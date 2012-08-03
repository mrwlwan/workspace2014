window.addEvent('domready', function(){

    var $setting = $('setting');

    var $conten_pane = $('main_content').getFirst('.inner_content');
    $conten_pane.set('load', {
        method: 'get',
        data: '',
        evalScripts: true,
        onRequest: function(){
            $conten_pane.empty();
            $conten_pane.addClass('loading');
        },
        onSuccess: function(e){
            $conten_pane.removeClass('loading');
        }
    });

    // 导航栏事件
    $('setting').addEvent('click:relay(.nav-list a)', function(e){
        e.stop();
        var $target = e.target;
        var $parent = $target.getParent('li');
        if($parent.hasClass('active')) return;

        //$('setting').getElements('.nav-list > li').removeClass('active');
        $setting.retrieve('active').removeClass('active');
        $setting.store('active', $parent);
        $parent.addClass('active');

        $conten_pane.load($target.get('href'));
    });
    $setting.store('active', $setting.getElement('.nav-list > li.active'));

    // 载入 active 选项的链接
    $conten_pane.load($setting.retrieve('active').getElement('a').get('href'));

///////////////////////////////////////////////////////////////////////////////////
// 文章管理
    $conten_pane.addEvent('submit:relay(#admin_entry_form)', function(e){
        var $target = e.target;
        if(!$target.retrieve('is_set_send')){
            $target.set('send', {
                onRequest: function(){
                    $('entry_list').addClass('loading');
                },
                onSuccess: function(data){
                    $('entry_list').set('html', data);
                }
            });
            $target.store('is_set_send', true);
        }
        $target.send();
        alert('submit');
        return false;
    });

    // 刷新按钮
    $conten_pane.addEvent('click:relay(#entry_refresh_btn)', function(e){
        $conten_pane.fireEvent('submit:relay(#admin_entry_form)', {target: $('admin_entry_form')});
    });

    // 文章类型选择事件
    $conten_pane.addEvent('change:relay(#entry_kind_select)', function(e){
        $conten_pane.fireEvent('submit:relay(#admin_entry_form)', {target: $('admin_entry_form')});
    });

    // page 事件
    $conten_pane.addEvent('change:relay(#entry_page)', function(e){
        alert('page change');
        var $page = $('entry_page');
        var $total_pages = $('entry_total_page');
        var cur_page = $page.get('value').toInt();
        var total_pages = $total_pages.get('text').toInt();
        if(cur_page<=1 || cur_page>=total_pages){
            $page.set('value', Math.max(1, cur_page.limit(1, total_pages)));
            return false;
        }
        $conten_pane.fireEvent('submit:relay(#admin_entry_form)', {target: $('admin_entry_form')});
        return false;
    });

    $conten_pane.addEvent('click:relay(#entry_page_nav a)', function(e){
        var $target = e.target;
        var $page = $('entry_page');
        var $total_pages = $('entry_total_page');
        var cur_page = $page.get('value').toInt();
        var total_pages = $total_pages.get('text').toInt();
        if(cur_page<=1 || cur_page>=total_pages) return false;
        if($target.hasClass('next')){
            $page.set('value', cur_page + 1);
        }else if($target.hasClass('previous')){
            $page.set('value', cur_page - 1);
        }
        $conten_pane.fireEvent('submit:relay(#admin_entry_form)', {target: $('admin_entry_form')});
        //$conten_pane.fireEvent('change:relay(#entry_page)', {target: $('#entry_page')});
        return false;
    });

});
