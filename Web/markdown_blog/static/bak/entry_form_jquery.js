function slug_process(str){
    return str.trim().replace(/\s+|\/+/gi, '_');
}

/////////////////////////////////////////////////////////////////////////////////////////
// 监视markdown的变化
function markdown_listener(e){
    $(e.target).data('is_changed', true);
}

// 预览listener
function markdown_preview_listener(e){
    var target = $(e.target);
    var form_content = $('#form_content');
    var pane = $(target.attr('href'));
    if(form_content.data('is_changed')){
        var markdown = $('#form_content').val();
        if(markdown){
            pane.empty().addClass('loading');
            $.post('/preview', data={
                'markdown': markdown,
                '_xsrf': $('#edit_form > input[name=_xsrf]').val()
            }, function(data){
                pane.removeClass('loading').html(data);
                form_content.data('is_changed', false);
                prettyPrint();
            });
        }else{
            $(target.attr('href')).html('');
            form_content.data('is_changed', false);
        }
    }
}

// 监视auto_slug的变化.
function auto_slug_listener(e){
    if($(e.target).prop('checked')){
        $('#slug').prop('disabled', true);
        $('#slug').val(slug_process($('#title').val()));
        slug_listener({'target': $('#slug')});
    }else{
        $('#slug').prop('disabled', false);
    }
}

// 监视title的变化
function title_listener(e){
    if($('#auto_slug').prop('checked')){
        $('#slug').val(slug_process($(e.target).val()));
        slug_listener({'target': $('#slug')});
    }
}

// 监视slug的变化
function slug_listener(e){
    if(!$(e.target).val()){
        $(e.target).parents('div.control-group').first().addClass('error');
        $('#slug_help').show();
        return;
    }
    $.get('/slug/' + $(e.target).val(), {'entry_key': $('#entry_key').val()}, function(data){
        var target = $(e.target);
        target.data('validate', Boolean(data.validate));
        form_validate_listener({'target': target});
    });
}

///////////////////////////////////////////////////////////////////////////////////////
$(function(){
    prettyPrint();

    //  监视markdown的变化.
    $('#form_content').on('change', markdown_listener);
    // markdown 预览.
    $('#form_tabs a:last').on('show', markdown_preview_listener);
    // 监视auto_slug的变化.
    $('#auto_slug').on('change', auto_slug_listener);
    // 监视title的变化
    $('#title').on('change', title_listener);
    // 监视slug的变化
    $('#slug').on('change', slug_listener);

    // 表单验证: required和validate
    $('#edit_form').on('blur', '.required:not(.xhr), .validate:not(.xhr)', form_validate_listener);
});

