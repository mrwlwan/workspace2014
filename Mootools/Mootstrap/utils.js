define(function(){
    return {
        'create_or_retrieve': function(el, name, cls, options){
            var obj = el.retrieve(name);
            if(!obj){
                obj = new cls(el, options);
                //el.store(name, obj);
            }
            return obj;
        },
        'get_target': function(el, data){
            data = data || 'data-target';
            var target = el.get(data);
            if(!target){
                target = el.get('href');
                if(target) target = target.replace(/.*(?=#[^\s]+$)/, ''); //strip for ie7
            }
            return $$(target)
        }
    }
});
