/* DROPDOWN CLASS DEFINITION */
define(['mootstrap/utils'], function(utils){
    var toggle = '[data-toggle=dropdown]'

    function get_parent(el){
        var selector = utils.get_targets(el)[0];
        if(!selector){
            selector = el.getParent();
        }
        return selector;
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
            if(!this.el.retrieve('dropdown')){
                this._add_events();
                this.el.store('dropdown', this);
            }
        },
        'toElement': function(){
            return this.container
        },
        '_add_events': function(){
            this.el.addEvent('click', this.toggle.bind(this));
            this.el.addEvent('keydown', this._keydown.bind(this));
        },
        '_keydown': function(e){
            if(!/(38|40|27)/.test(e.code)) return;
            if(this.el.match('.disabled, :disabled')) return;
            var is_active = this.is_active();
            if(!is_active||(is_active&&e.code==27)){
                if(e.code==27) this.el.focus();
                return this.toggle();
            }
            var $items = this.container.getElements('[role=menu] li:not(.divider):visible a');
            if(!$items.length) return;
            var index = $items.indexOf($items.filter(':focus'));
            if(e.code==38&&index>0) index--;                // up
            if(e.code==40&&index<$items.length-1) index++;  // down
            if(!~index) index = 0;
            $items[index].focus();
            return false; // Stop event bubbled.
        },
        'is_active': function(){
            return this.container.hasClass('open');
        },
        'toggle': function(e){
            if(this.el.match('.disable, :disabled')) return
            var is_active = this.is_active();
            clear_menus();
            if(!is_active){
                this.container.addClass('open');
            }
            this.el.focus();
            return false; // Stop event bubbled.
        }
    });


    var $body = $$('body');
    document.addEvent('click', clear_menus);
    $body.addEvent('click:relay(.dropdown form)', function(e){e.stopPropagation();});
    $body.addEvent('click:relay('+toggle+')', function(e){
        e.stop();
        //utils.create_or_retrieve(this, 'dropdown', Dropdown).toggle(e);
        new Dropdown(this).toggle(e);
    });
    $body.addEvent('keydown:relay('+toggle + ', [role=menu])', function(e){
        e.stop();
        //utils.create_or_retrieve(this, 'dropdown', Dropdown)._keydown(e);
        new Dropdown(this).toggle(e);
    });

    return Dropdown
});
