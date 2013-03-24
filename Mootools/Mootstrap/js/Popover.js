/* POPOVER CLASS DEFINITION */
define(['mootstrap/utils', 'mootstrap/Tooltip'], function(utils, Tooltip){
    var Popover = new Class({
        Extends: Tooltip, // 继承自Tooltip类
        //Implements: [Options, Events],
        options: {
            'transition': true,
            'placement': 'right',
            'selector': false,
            'template': '<div class="popover"><div class="arrow"></div><h3 class="popover-title"></h3><div class="popover-content"></div></div>',
            'trigger': 'click',
            'title': '', // 标题
            'content': '', // 内容
            'opacity': 1,
            'delay': 0,
            'duration': 0, // 显示停留时间, <=0 表示一直显示
            'content_type': 'text', 
            'container': false // 对于单个el, container有时也要显式指定(Parent对象非static定位的时候), 否则定位有误
        },
        'initialize': function(el, options){
            this.setOptions(options)
            this.parent(el, options);
            this.type = 'popover';
            //if(!this.options.selector) this.fix_title();
        },
        'get_content': function(el){
            var el = el || this.el;
            var title = el.retrieve('content');
            if(title==null){
                title = Function.from(this.options.content || el.get('data-content'));
                el.store('content', title);
            }
            return title(el);
        },
        'has_content': function(el){
            el = el || this.el;
            return this.get_title(el) || this.get_content(el);
        },
        'set_content': function(el){
            el = el || this.el;
            var tip = this.get_tip(el);
            var content = this.get_content(el);
            var title = this.get_title(el);
            tip.getElement('.popover-title').set(this.options.content_type, title);
            tip.getElement('.popover-content').set(this.options.content_type, content);
            utils.remove_classes(el, 'fade in top bottom left right');
            return tip;
        }
    });

    return Popover;
});

