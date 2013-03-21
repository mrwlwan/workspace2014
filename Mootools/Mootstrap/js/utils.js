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
        },
        'json': function(value){
            return JSON.decode(value);
        }
    };

    function get_data(el, name, type){
       var value = el.get('data-'+name);
       return value==null ? null : (type ? data_process[type](value) : value);
    }

    function split_classes(classes){
        return classes.trim().split(/\s+/);
    }

    function has_classes(el, classes){
        return split_classes(classes).every(function(item){
            return el.hasClass(item);
        });
    }

    function add_classes(el, classes){
        split_classes(classes).each(function(item){
            el.addClass(item);
        });
        return el;
    }

    function remove_classes(el, classes){
        split_classes(classes).each(function(item){
            el.removeClass(item);
        });
        return el;
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
        },
        'is_visible': function(el){
            if(el.getStyle('visibility')!='hidden' && el.getStyle('display')!='none'){
                var size = el.getSize();
                return size.x * size.y >0
            }
            return false;
        },
        'has_classes': has_classes,
        'add_classes': add_classes,
        'remove_classes': remove_classes,
        'back_drop': function(el, options){
            el = el || document.body;
            var new_el = new Element('div', {'class': 'modal-backdrop'});
            options.classes && add_classes(new_el, options.classes);
            options.styles && el.setStyles(styles);
            document.body.grab(new_el);
            new_el.addEvent('click', function(){
                options.callback && options.callback();
                new_el.fade('out');
                new_el.destroy();
            });
            new_el.fade(0.8);
            return new_el;
        },
        // 相当于jQuery的one
        'one': function(el, event_type, fn){
            var temp_fn = function(){
                el.removeEvent(event_type, temp_fn);
                return fn.attempt(arguments);
            };
            el.addEvent(event_type, temp_fn);
            return el;
        }
    }
});
