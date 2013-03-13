define(function(){
    var data_process = {
        'string': function(value){return value},
        'int': function(value){return parseInt(value.trim())},
        'float': function(value){return parseFloat(value.trim())},
        'bool': function(value){
            switch(value.trim().toLowerCase()){
                case 'false':
                    return false;
                case '0':
                    return false;
                case '':
                    return false;
            }
            return true;
        }
    };
    function get_data(el, name, type){
       var value = el.get('data-'+name);
       return value==null ? null : (type ? data_process[type](value) : value);
    }

    return {
        'create_or_retrieve': function(el, name, cls, options){
            var obj = el.retrieve(name);
            if(!obj){
                obj = new cls(el, options);
                //el.store(name, obj);
            }
            return obj;
        },
        'get_targets': function(el, data){
            data = data || 'data-target';
            var target = el.get(data);
            if(!target){
                target = el.get('href');
                if(target) target = target.replace(/.*(?=#[^\s]+$)/, ''); //strip for ie7
            }
            return $$(target)
        },
        'get_data': get_data,
        'get_options': function(el, names){
            var options = {}
            Object.each(names, function(type, name){
                var value = get_data(el, name, type);
                if(value!=null) options[name] = value;
            });
            return options;
        }
    }
});
