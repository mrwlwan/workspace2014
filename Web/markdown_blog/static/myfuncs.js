// Check the form with validata class.
function form_validate_listener(e){
    var $target = e.target;
    if(e.type=='change'){
        $target.store('is_changed', true);
    }
    var $control_group = $target.getParent('.control-group');
    var $info = $target.getNext('.help-block');
    var validate = false;
    if($target.hasClass('required')){
        if($target.get('value').trim()){
            validate = true;
        }
    }else{
        validate=true;
    }
    if($target.hasClass('validate') && $target.retrieve('validate')==false){
        validate = false;
    }
    if(validate){
        $control_group.removeClass('error');
        $info.addClass('hide');
        $info.fade('out');
    }else{
        $control_group.addClass('error');
        $info.removeClass('hide');
        $info.fade('in');
    }
}
