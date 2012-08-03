// Check the form with validata class.
function form_validate_listener(e){
    var target = $(e.target);
    if(e.type=='change'){
        target.data('is_changed', true);
    }
    var control_group = target.parents('.control-group').first();
    var info = target.nextAll('.help-block').first();
    var validate = false;
    if(target.hasClass('required')){
        if(target.val().trim()){
            validate = true;
        }
    }else{
        validate=true;
    }
    if(target.hasClass('validate') && target.data('validate')==false){
        validate = false;
    }
    if(validate){
        control_group.removeClass('error');
        info.hide();
    }else{
        control_group.addClass('error');
        info.show();
    }
}
