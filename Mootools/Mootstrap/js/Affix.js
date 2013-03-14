/* AFFIX CLASS DEFINITION */
define(['./utils.js'], function(utils){
    var Affix = new Class({
        Implements: Options,
        options: {
            'offset': 0
        },
        'initialize': function(el, options){
            this.el = $(el);
            this.setOptions(options);
            // el原本位置
            this.original_position = this.el.getPosition();
            this.offset = this._offset(this.options.offset);
            this._previous_state = 'top';
            this._previous_offset = {};
            if(!this.el.retrieve('affix')){
                this._add_events();
                this.el.store('affix', this);
            }
            // 初始化位置
            this.check_position();
        },
        'toElement': function(){
            return this.el;
        },
        '_add_events': function(){
            window.addEvent('scroll', this.check_position.bind(this));
        },
        '_offset': function(data){
            var offset = {};
            if(typeOf(offset)=='object'){
                offset.top = Function.from(data.top || 0);    
                offset.bottom = Function.from(data.bottom || 0);    
            }else{
                offset.top = offset.bottom = Function.from(data);
            }
            return offset;
        },
        'position': function(state, offset){
            switch(state){
                case 'top':
                    this.el.removeClass('affix').setStyle('top', null).setStyle('bottom', null);
                    break;
                case 'affix':
                    this.el.addClass('affix').setStyle('top', offset.top).setStyle('bottom', null);
                    break;
                case 'bottom':
                    this.el.addClass('affix').setStyle('top', null).setStyle('bottom', offset.bottom);
            }
        },
        'check_position': function(){
            // 判断是否隐藏
            if(!utils.is_visible(this.el)) return;
            //var scroll_height = document.getSize().y;
            var scroll_height = window.getScrollSize().y - window.getSize().y;
            var scroll_top = window.getScroll().y;
            var size = this.el.getSize();
            var state;
            var offset = {'top': this.offset.top(), 'bottom': this.offset.bottom()};
            var affix;

            if(scroll_top <= this.original_position.y - offset.top){
                state = 'top';
            }else if(scroll_top <= scroll_height - offset.bottom - size.y){
                state = 'affix';
            }else{
                state = 'bottom';
            }
            if(state!=this._previous_state || offset.top!=this._previous_offset.top || offset.bottom!=this._previous_offset.bottom){
                this.position(state, offset);
            }
            this._previous_state = state;
            this._previous_offset = offset;
        }
    });

    window.addEvent('domready', function(e){
        $$('[data-spy="affix"]').each(function(spy){
            var options = {}
            var offset = {};
            var top = utils.get_data('offset-top');
            top && (offset['top'] = top);
            var bottom = utils.get_data('offset-bottom');
            bottom && (offset['bottom'] = bottom);
            Object.getLength(offset) && (options['offset'] = offset);
            new Affix(spy, options);
        });
    });

    return Affix;
});
