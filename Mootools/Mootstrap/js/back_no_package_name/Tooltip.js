/* TOOLTIP CLASS DEFINITION */
define(['./utils.js', './more/Elements_from.js'], function(utils){
    var Tooltip = new Class({
        Implements: [Options, Events],
        options: {
            'transition': true,
            'placement': 'top',
            'selector': false,
            'template': '<div class="tooltip"><div class="tooltip-arrow"></div><div class="tooltip-inner"></div></div>',
            'trigger': 'hover focus',
            'title': '',
            'opacity': 0.8,
            'delay': 0,
            'duration': 0, // 显示停留时间, <=0 表示一直显示
            'content_type': 'text', 
            'container': false, // 对于单个el, container有时也要显式指定, 否则定位有误
        },
        'initialize': function(el, options){
            this.type = 'tooltip';
            this.el = $(el);
            this.setOptions(options);
            this.triggers = this.options.trigger.split(' ');
            if(typeOf(this.delay)!='object'){
                this.delay = {'show': this.options.delay, 'hide': this.options.delay};
            }
            this.placement = Function.from(this.options.placement);
            this.enabled = true
            if(!this.el.retrieve(this.type)){
                this._add_events();
                this.el.store(this.type, this);
            }
            //if(!this.options.selector) this.fix_title();
        },
        'toElement': function(){
            return this.el;
        },
        '_get_event_type': function(type){
            return this.options.selector ? type+':relay('+this.options.selector+')' : type;
        },
        '_add_events': function(){
            var thisobj = this;
            this.triggers.each(function(trigger){
                if(trigger=='click'){
                    thisobj.el.addEvent(thisobj._get_event_type('click'), function(e, target){
                        e.preventDefault();
                        thisobj.toggle(target);
                    });
                }else if(trigger!='manual'){
                    var event_in = trigger == 'hover' ? 'mouseenter' : 'focus';
                    var event_out = trigger == 'hover' ? 'mouseleave' : 'blur';
                    thisobj.el.addEvent(thisobj._get_event_type(event_in), function(e, target){
                        e.preventDefault();
                        thisobj.show(target);
                    });
                    thisobj.el.addEvent(thisobj._get_event_type(event_out), function(e, target){
                        thisobj.hide(target);
                    });
                }
            });
        },
        'fix_title': function(el){
            el = el || this.el;
            var title = el.get('title');
            if(title){
                el.set({
                    'data-original-title': title,
                    'title': ''
                });
            }
        },
        'get_placement': function(el){
            el = el || this.el;
            return this.placement(el);
        },
        'get_container': function(){
            return this.options.container || (this.options.selector ? this.el : null);
        },
        'get_title': function(el){
            var el = el || this.el;
            var title = el.retrieve('title');
            if(title==null){
                title = Function.from(this.options.title || el.get('title') || el.get('data-original-title'));
                this.fix_title(el);
                el.store('title', title);
            }
            return title(el);
        },
        'has_content': function(el){
            el = el || this.el;
            return this.get_title(el);
        },
        'get_tip': function(el){
            var el = el || this.el;
            var tip = el.retrieve('tip');
            if(!tip){
                tip = Elements.from(this.options.template)[0];
                el.store('tip', tip)
            }
            return tip;
        },
        'set_content': function(el){
            el = el || this.el;
            var tip = this.get_tip(el);
            var title = this.get_title(el);
            tip.getElement('.tooltip-inner').set(this.options.content_type, title);
            utils.remove_classes(el, 'fade in top bottom left right');
            return tip;
        },
        'inject_tip': function(el, tip){
            var el = el || this.el;
            var tip = tip || this.get_tip(el);
            var container = this.get_container();
            if(container){
                tip.inject(container);
            }else{
                tip.inject(el, 'after');
            }
            var placement = this.get_placement(el);
            tip.addClass(placement);
            var el_coordinates = el.getCoordinates(container || el.getOffsetParent() || document.body);
            var tip_size = tip.getSize();
            var tip_pos = {};
            switch(placement){
                case 'bottom':
                    tip_pos = {'top': el_coordinates.top + el_coordinates.height, 'left': el_coordinates.left + el_coordinates.width / 2 - tip_size.x / 2};
                    break;
                case 'top':
                    tip_pos = {'top': el_coordinates.top - tip_size.y, 'left': el_coordinates.left + el_coordinates.width / 2 - tip_size.x / 2};
                    break;
                case 'left':
                    tip_pos = {'top': el_coordinates.top + el_coordinates.height / 2 - tip_size.y / 2, 'left': el_coordinates.left - tip_size.x};
                    break;
                case 'right':
                    tip_pos = {'top': el_coordinates.top + el_coordinates.height / 2 - tip_size.y / 2, 'left': el_coordinates.left + el_coordinates.width};
                break;
            }
            tip.setStyles(tip_pos);
        },
        '_transition': function(tip, arg, callback){
            var thisobj = this;
            var fx = tip.retrieve('fx');
            var timeout = tip.retrieve('timeout');
            fx && fx.cancel();
            timeout && clearTimeout(timeout);
            fx = new Fx.Tween(tip, {
                'property': 'opacity',
                'duration': thisobj.options.transition && 200 || 0,
                'onComplete': function(){
                    callback && callback();
                }
            });
            tip.store('fx', fx);
            tip.store('timeout', setTimeout(function(){
                fx.start(arg);
            }, this.delay.show));
        },
        'show': function(el){
            var thisobj = this;
            var el = el || this.el;
            if(!this.enabled || !this.has_content(el)) return;
            // show事件触发
            this.fireEvent('show', el);
            var tip = this.get_tip(el);
            this.set_content(el);
            tip.setStyles({
                'display': 'block'
            });
            tip.addClass('in');
            this.inject_tip(el, tip);
            tip.setStyle('opacity', 0);
            this._transition(tip, [0, this.options.opacity], function(){
                thisobj.fireEvent('shown', el);
                if(thisobj.options.duration>0){
                    tip.store('timeout', setTimeout(function(){
                        thisobj.hide(el);
                    }, thisobj.options.duration));
                }
            });
        },
        'hide': function(el){
            var thisobj = this;
            el = el || this.el;
            var tip = this.get_tip(el);
            if(!tip.hasClass('in')) return;
            this.fireEvent('hide', el);
            tip.setStyle('opacity', this.options.opacity);
            this._transition(tip, [this.options.opacity, 0], function(){
                tip.removeClass('in');
                tip.dispose();
                thisobj.fireEvent('hidden', el);
            });
        },
        'enable': function(){
            this.enabled = true;
        },
        'disable': function(){
            this.enabled = false;
        },
        'toggle_enabled': function(){
            this.enabled = !this.enabled;
        },
        'toggle': function(e, target){
            e && e.preventDefault();
            var el = target || this.el;
            this.get_tip(el).hasClass('in') ? this.hide(el) : this.show(el);
        },
        'destroy': function(){
        }
    });

    return Tooltip;
});
