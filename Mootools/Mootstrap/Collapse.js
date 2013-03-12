/* COLLAPSE CLASS DEFINITION */
define(['./utils.js'], function(utils){
    var Collapse = new Class({
        Implements: Options,
        options: {
            'toggler_selector': '.accordion-toggle',
            'content_selector': '.accordion-body',
            'always_hide': false
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
            return this.el.getParent('accordion-group');
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
            return utils.get_target(toggler)[0] || toggler.getParent().getNext();
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
            if(this.is_transitioning() || this.is_active(content)) return;
            this.transition(this.get_active_contents(), [content]);
        },
        'hide': function(content){ 
            if(this.is_transitioning() || !this.is_active(content)) return;
            this.transition([content]);
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
                    'duration': 250,
                    'onComplete': function(){
                        item.removeClass('in');
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
                    'duration': 250,
                    'onStart': function(){
                        item.addClass('in');
                    }
                }).start(margin_top));
            });
        }
    });


    $$('body').addEvent('click:relay([data-toggle=collapse])', function(e){
        var container = utils.get_target(this, 'data-parent')[0] || this.getParent('.accordion');
        var always_hide = this.get('data-always_hide') && true || false;
        var collapse = new Collapse(container, {'always_hide': !always_hide});
        collapse.toggle(collapse.get_content(this));
    });

    return Collapse;
})
