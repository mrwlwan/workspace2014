function slug_process(str){
    return str.trim().replace(/\s+|\/+/gi, '_');
}

/////////////////////////////////////////////////////////////////////////////////////////
// 监视markdown的变化
function markdown_listener(e){
    e.target.retrieve('is_changed', true);
}

// 预览listener
function markdown_preview_listener(e){
    var $target = e.target;
    var $form_content = $('form_content');
    var $pane = $$($target.get('href'))[0];
    if($form_content.retrieve('is_changed')){
        var markdown = $('form_content').get('value');
        if(markdown){
            $pane.empty().addClass('loading');
            new Request({
                url: '/preview',
                data: {
                    'markdown': markdown,
                    '_xsrf': $('edit_form').getFirst('input[name=_xsrf]').get('value')
                },
                onSuccess: function(data){
                    $pane.removeClass('loading').set('html', data);
                    $form_content.store('is_changed', false);
                    prettyPrint();
                }
            }).post();
        }else{
            $pane.set('html', '');
            $form_content.store('is_changed', false);
        }
    }
}

// 监视auto_slug的变化.
function auto_slug_listener(e){
    if(e.target.get('checked')){
        $('slug').set('disabled', true);
        $('slug').set('value', slug_process($('title').get('value')));
        slug_listener({'target': $('slug')});
    }else{
        $('slug').set('disabled', false);
    }
}

// 监视title的变化
function title_listener(e){
    if($('auto_slug').get('checked')){
        $('slug').set('value', slug_process(e.target.get('value')));
        slug_listener({'target': $('slug')});
    }
}

// 监视slug的变化
function slug_listener(e){
    if(!e.target.get('value').trim()){
        e.target.getParent('div.control-group').addClass('error');
        $('slug_help').removeClass('hide');
        $('slug_help').fade('in');
        return;
    }
    new Request.JSON({
        url: '/slug/' + e.target.get('value'),
        data: {'entry_key': $('entry_key').get('value')},
        onSuccess: function(data){
            var $target = e.target;
            $target.store('validate', Boolean(data.validate));
            form_validate_listener({'target': $target});
        }
    }).get();
}

function slug_blur_listener(e){
    if(!e.target.get('value').trim() && $('slug_help').hasClass('hide')){
        e.target.getParent('div.control-group').addClass('error');
        $('slug_help').removeClass('hide');
        $('slug_help').fade('in');
    }
}
///////////////////////////////////////////////////////////////////////////////////////
window.addEvent('domready', function(){
    prettyPrint();

    //  监视markdown的变化.
    $('form_content').addEvent('change', markdown_listener);
    // markdown 预览.
    $$('#form_tabs a').getLast().addEvent('click', markdown_preview_listener);
    // 监视auto_slug的变化.
    $('auto_slug').addEvent('change', auto_slug_listener);
    // 监视title的变化
    $('title').addEvent('change', title_listener);
    // 监视slug的变化
    $('slug').addEvent('change', slug_listener);
    $('slug').addEvent('blur', slug_blur_listener);

    // 表单验证: required和validate
    $('edit_form').addEvent('blur:relay(.required:not(.xhr), .validate:not(.xhr))', form_validate_listener);
});

