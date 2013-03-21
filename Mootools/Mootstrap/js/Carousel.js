/* CAROUSEL CLASS DEFINITION */
define(['./utils.js', './more/Elements_from.js'], function(utils){
    var Carousel = new Class({
        Implements: [Options, Events],
        options: {
            'interval': 5000,
            'pause': 'hover',
            'duration': 1000,
            'transition': true
        },
        'initialize': function(container, options){
            this.container = container;
            this.indicator = this.container.getElement('.carousel-indicators');
            this.$navs = this.container.getElements('[data-slide]');
            this.items_container = this.container.getElement('.carousel-inner');
            this.setOptions(options);
            if(!this.container.retrieve('carousel')){
                this._add_events();
                this.container.store('carousel', this);
            }
            this.paused = true;
            this.interval = null;
            this.fx = null;

            this.cycle();
        },
        'toElement': function(){
            return this.container;
        },
        '_add_events': function(){
            var thisobj = this;
            if(this.options.pause=='hover'){
                this.container.addEvent('mouseenter', this.pause.bind(this));
                this.container.addEvent('mouseleave', this.cycle.bind(this));
            }else{
                this.container.addEvent(this.options.pause, this.toggle.bind(this));
            }
            this.container.addEvent('click:relay([data-slide])', function(e){
                e.preventDefault();
                thisobj.slide(this.get('data-slide'));
            });
            this.container.addEvent('click:relay([data-slide-to])', function(e){
                thisobj.to(parseInt(this.get('data-slide-to')));
            });
        },
        'cycle': function(){
            if(this.paused && this.options.interval){
                this.paused = false;
                if(this.interval) clearInterval(this.interval);
                this.interval = this.slide.periodical(this.options.interval, this, 'next');
            }
            return this;
        },
        'get_active_item': function(){
            var active;
            var $items = this.items_container.getChildren('.item');
            for(var i=0;i<$items.length;i++){
                active = $items[i];
                if(active.hasClass('active')){
                    return [active, i, $items];
                }
            }
            return [null, -1, null];
        },
        'to': function(pos){
            var thisobj = this;
            var temp = this.get_active_item();
            var active = temp[0];
            var index = temp[1];
            var $items = temp[2];
            if(pos<0 || pos > ($items.length - 1)) return;
            if(index==pos){
                return;
            }
            return this.slide(pos > index? 'next' : 'prev', $($items[pos]))
        },
        // 暂停循环; 如果没有循环在运行, 则不执行
        'pause': function(e){
            if(this.interval){
                clearInterval(this.interval)
                this.interval = null
                this.paused = true;
            }
            return this;
        },
        'slide_indicator': function(next_index){
            if(this.indicator){
                this.indicator.getElement('.active').removeClass('active');
                var next_indicator_item = this.indicator.getChildren()[next_index];
                next_indicator_item && next_indicator_item.addClass('active');
            }
        },
        'slide': function(type, next){
            // 等待动画完成
            if(this.fx && this.fx.isRunning()){
                return utils.one(this, 'slid', this.slide.pass([type, next], this));
            }
            if(next) this.pause();
            var direction = type == 'next' ? 'left' : 'right';
            var fallback  = type == 'next' ? 'first' : 'last';
            var thisobj = this;
            var temp = this.get_active_item();
            var active = temp[0];
            var index = temp[1];
            var $items = temp[2];
            if(!next){
                switch(type){
                    case 'next':
                        next = active.getNext() || $items[0];
                        break;
                    case 'prev':
                        next = active.getPrevious() || $items[$items.length-1];
                        break;
                }
            }
            if(next.hasClass('active')) return;
            this.fireEvent('slide', [active, next, direction]);
            var next_index = $items.indexOf(next);
            if(this.options.transition){
                this.transition(active, next, next_index, function(){
                    thisobj.fireEvent('slid', [active, next, direction]);
                });
            }else{
                active.removeClass('active');
                this.slide_indicator(next_index)
                next.addClass('active');
                thisobj.fireEvent('slid', [active, next, direction]);
            }
            // 重新进入循环
            if(this.paused) this.cycle();
        },
        'transition': function(active, next, next_index, callback){
            var thisobj = this;
            this.fx = new Fx.Tween(active, {
                'property': 'opacity',
                'duration': this.options.duration*0.4,
                'onComplete': function(){
                    next.setStyle('display', 'block');
                    active.setStyle('display', 'none');
                    active.removeClass('active');
                    next.addClass('active');
                    thisobj.slide_indicator(next_index);

                    thisobj.fx = new Fx.Tween(next, {
                        'property': 'opacity',
                        'duration': thisobj.options.duration*0.6,
                        'onComplete': function(){
                            thisobj.fx = null;
                            callback && callback();
                        }
                    });
                    thisobj.fx.start(0.8, 1);
                }
            });
            this.fx.start(1, 0);
        },
        'toggle': function(){
            if(this.passed){
                this.cycle();
            }else{
                this.pause();
            }
        }
    });

    document.body.addEvent('click:relay([data-slide], [data-slide-to])', function(e, target){
        var container = utils.get_targets(this)[0] || this.getParent('.carousel');
        if(container.retrieve('carousel')) return;
        var options;
        if(container.hasClass('slide')) options = {'transition': true};
        Object.append(options, utils.get_options({'interval': 'int', 'pause': 'string', 'transition': 'bool', 'duration': 'int'}));
        var carousel = new Carousel(container, options);
        var index = this.get('data-slide-to');
        if(index){
            carousel.to(parseInt(index));
        }else{
            carousel.slide(this.get('data-slide'));
        }
    });    

    return Carousel;
});
