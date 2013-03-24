/* COLLAPSE CLASS DEFINITION */
define(['mootstrap/utils'], function(utils){
    var Collapse = new Class({
        Implements: [Options, Events],
        options: {
            'toggler_selector': '.accordion-toggle',
            'content_selector': '.accordion-body',
            'always_hide': false,
            'duration': 250,
            'transition': true
        },
        'initialize': function(container, options){
            this.container = $(container);
            this.setOptions(options);
            this.$togglers = this.options.togglers && $$(this.options.togglers);
            this.$contents = this.options.contents && $$(this.options.contents);
            if(!this.container.retrieve('collapse')){
                this._add_events();
                this.container.store('collapse', this);
            }
            this.transition_list = [];
        },
        'toElement': function(){
            return this.container;
        },
        '_add_events': function(){
            var thisobj = this;
            this.container.addEvent('click:relay([data-toggle=collapse])', function(e){
                e.stop();
                thisobj.toggle(thisobj.get_content(this));
                document.fireEvent('click');
                return false;
            });                
        },
        // 返回所有togglers
        'get_togglers': function(){
            return this.$togglers || this.container.getElements(this.options.toggler_selector);
        },
        // 返回指定的content
        'get_content': function(toggler){
            return utils.get_targets(toggler)[0] || toggler.getParent().getNext();
        },
        // 返回所有contents
        'get_contents': function(){
            return this.$contents || this.container.getElements(this.options.content_selector);
        },
        // 横向, 暂时未支持功能
        'dimension': function(){
            return this.body.hasClass('width') ? 'width' : 'height';
        },
        'get_active_contents': function(){
            if(this.$contents){
                return this.$contents.filter(function(item){
                    item.match('.in');
                });
            }else{
                return this.container.getElements('> .accordion-group > .in');
            }
        },
        // 判断content是否显示中
        'is_active': function(content){
            return content.match('.in');
        },
        // 判断动画是否在进行中
        'is_transitioning': function(content){
            return this.transition_list.some(function(item){
                return item.isRunning();
            });
        },
        'show': function(content){
            var thisobj = this;
            if(!this.is_active(content)){
                if(this.options.transition){
                    this.is_transitioning() || this.transition(this.get_active_contents(), [content]);
                }else{
                    thisobj.fireEvent('show', content);
                    this.get_active_contents().each(function(item){
                        thisobj.fireEvent('hide', item);
                        item.removeClass('in');
                        thisobj.fireEvent('hiden', item);
                    });
                    content.addClass('in');
                    thisobj.fireEvent('shown', content);
                }
            }
        },
        'hide': function(content){ 
            if(this.is_active(content)){
                if(this.options.transition){
                    this.is_transitioning() || this.transition([content]);
                }else{
                    thisobj.fireEvent('hide', content);
                    content.addClass('in');
                    thisobj.fireEvent('hiden', content);
                }
            }
        },
        'toggle': function(content){
            if(this.is_active(content)){
                this.options.always_hide && this.hide(content);
            }else{
                this.show(content);
            }
            return false;
        },
        // 动画过渡效果
        'transition': function($hide_contents, $show_contens){
            var thisobj = this;
            this.transition_list.empty();
            $hide_contents && $hide_contents.each(function(item){
                var target = item.getChildren()[0];
                target.store('margin-top', target.getStyle('margin-top') || 0);
                thisobj.transition_list.push(new Fx.Tween(target, {
                    'property': 'margin-top',
                    'duration': thisobj.options.duration,
                    'onStart': function(){
                        thisobj.fireEvent('hide', item);
                    },
                    'onComplete': function(){
                        item.removeClass('in');
                        thisobj.fireEvent('hiden', item);
                    }
                }).start(-target.getSize().y));
            });
            $show_contens && $show_contens.each(function(item){
                var target = item.getChildren()[0];
                var margin_top = target.retrieve('margin-top');
                if(!margin_top){
                    margin_top = target.getStyle('margin-top') || 0;
                    target.setStyle('margin-top', -target.getSize().y);
                    target.store('margin-top', margin_top);
                }
                thisobj.transition_list.push(new Fx.Tween(target, {
                    'property': 'margin-top',
                    'duration': thisobj.options.duration,
                    'onStart': function(){
                        item.addClass('in');
                        thisobj.fireEvent('show', item);
                    },
                    'onComplete': function(){
                        thisobj.fireEvent('shown', item);
                    }
                }).start(margin_top));
            });
        }
    });


    $$('body').addEvent('click:relay([data-toggle=collapse])', function(e){
        e.preventDefault();
        var container = utils.get_targets(this, 'data-parent')[0] || this.getParent('.accordion');
        //var always_hide = this.get('data-always_hide');
        var options = utils.get_options(container, {'always_hide': 'bool', 'duration': 'int', 'transition': 'bool'});
        var collapse = new Collapse(container, options);
        collapse.toggle(collapse.get_content(this));
    });

    return Collapse;
})
