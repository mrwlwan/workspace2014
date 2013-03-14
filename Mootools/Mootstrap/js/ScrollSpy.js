/* SCROLLSPY CLASS DEFINITION */
define(['./utils.js'], function(utils){
    var ScrollSpy = new Class({
        Implements: Options,
        options: {
            'offset': 10
        },
        'initialize': function(container, options){
            this.container = $(container);
            this.nav_container = utils.get_targets(this.container)[0];
            this.setOptions(options);
            // 初始化
            this.refresh();
            this.process();
            if(!this.container.retrieve('scrollspy')){
                this._add_events();
                this.container.store('scrollspy', this);
            }
        },
        'toElement': function(){
            return this.container;
        },
        '_add_events': function(){
            (this.container.get('tag')=='body' ? window : this.container).addEvent('scroll', this.process.bind(this));
        },
        // 初始化数据, 文档内容有所变化, 应该显式调用此方法
        'refresh': function(){
            var thisobj = this;
            var navs = this.nav_container.getElements('li a:not([href$=#])');
            var top_with_index = {}
            this.offset_tops = [];

            navs.each(function(item, index){
                var target = utils.get_targets(item)[0];
                var offset_top = target.getPosition(thisobj.container).y-thisobj.options.offset;
                thisobj.offset_tops.push(offset_top);
                top_with_index[offset_top] = index;
            });

            this.offset_tops = this.offset_tops.sort(function(a,b){return a-b;});
            this.nav_wraps = this.offset_tops.map(function(item){         
                return navs[top_with_index[item]].getParents('li');
            });
        },
        'get_index': function(scroll_top){
            var index = this.offset_tops.length - 1;
            for(var i=0; i<this.offset_tops.length; i++){
                if(scroll_top<this.offset_tops[i]){
                    index = i-1;
                    break;
                }
            }
            return index;
        },
        'process': function(){
            var scroll_top = this.container.getScroll().y;
            var index = this.get_index(scroll_top);
            if(index != this._previous_index){
                this._previous_nav_wraps && this._previous_nav_wraps.removeClass('active');
                if(index>=0){
                    this._previous_nav_wraps = this.nav_wraps[index].addClass('active');
                }
                this._previous_index = index;
            }
        }           
    });

    window.addEvent('domready', function(){
        $$('[data-spy=scroll]').each(function(item){
            var options = utils.get_options({'offset': 'int'});
            new ScrollSpy(item, options);
        });
    });

    return ScrollSpy;
});
        
            
