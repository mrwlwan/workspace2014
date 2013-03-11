 /* DROPDOWN CLASS DEFINITION */
define(function(){
    var toggle = '[data-toggle=dropdown]'

    function get_parent(el){
        var selector = el.get('data-target');
        if(!selector){
            selector = el.get('href');
            selector = selector && /#/.test(selector) && selector.replace(/.*(?=#[^\s]*$)/, ''); //strip for ie7
        }
        var $selector = selector && $$(selector);
        if(!$selector||!$selector.length){
            $selector = el.getParent();
        }
        return $selector
    }

    function clear_menus(e){
        $$(toggle).each(function(el){
            get_parent(el).removeClass('open');
        });
    }

    
    var Dropdown = new Class({
        Implements: Options,
        options: {},
        'initialize': function(el, options){
            this.el = $(el);
            this.container = get_parent(this.el);
            this.setOptions(options);
            this._add_events();
        },
        'toElement': function(){
            return this.container
        },
        '_add_events': function(){
            var thisobj = this;
            this.el.addEvent('click', this.toggle.bind(this));
            //this.el.addEvent('keydown', this._keydown.bind(this));
            document.addEvent('click', function(e){
                thisobj.container.removeClass('open');
            });
        },
        '_keydown': function(e){
            //alert(e.code);
            if(!/(38|40|27)/.test(e.code)) return;
            e.stop();
            if(this.el.match('.disabled, :disabled')) return;
            var is_active = this.is_active();
            if(!is_active||(is_active&&e.code==27)){
                if(e.code==27) this.el.focus();
                return this.toggle();
            }
            var $items = this.container.getElements('[role=menu] li:not(.divider):visible a');
            if(!$items.length) return;
            var index = $items.indexOf($items.filter(':focus'));
            if(e.code==38&&index>0) index--;                                        // up
            if(e.code==40&&index<$items.length-1) index++;                        // down
            if(!~index) index = 0;
            $items[index].focus();
        },
        'is_active': function(){
            return this.container.hasClass('open');
        },
        'toggle': function(e){
            if(this.el.match('.disable, :disabled')) return
            var is_active = this.is_active();
            clear_menus();
            if(!is_active){
                this.container.toggleClass('open');
            }
            this.el.focus();
            return false; // Stop event bubbled.
        }
    });

    function create_or_retrieve(el){
        var dropdown = el.retrieve('dropdown');
        if(!dropdown){
            dropdown = new Dropdown(el);
            el.store('dropdown', dropdown)
        }
        return dropdown;
    }

    document.addEvent('click', clear_menus);
    document.addEvent('click:relay(.dropdown form)', function(e){e.stopPropagation();});
    document.addEvent('click', function(e){e.stopPropagation();});
    document.addEvent('click:relay('+toggle+')', function(e){
        create_or_retrieve(this).toggle();
    });
    document.addEvent('keydown:relay('+toggle + ', [role=menu])', function(e){
        create_or_retrieve(this)._keydown(e);
    });

    return Dropdown
});
