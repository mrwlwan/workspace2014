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
                thisobj[this.get('data-slide')]();
            });
            this.container.addEvent('click:relay([data-slide-to])', function(e){
                thisobj.to(parseInt(this.get('data-slide-to')));
            });
        },
        'transitioning': function(){
            return this.fx && this.fx.isRunning();
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
        'cycle': function(){
            if(this.options.interval){
                this.paused = false;
                if(this.interval) clearInterval(this.interval);
                this.interval = this.next.periodical(this.options.interval, this, true);
            }
            return this;
        },
        'next': function(cycle){
            var temp = this.get_active_item();
            var active = temp[0];
            var next = active.getNext() || temp[2][0];
            var next_index = temp[2].indexOf(next);
            return this.slide('next', active, next, next_index, cycle);
        },
        'prev': function(cycle){
            var temp = this.get_active_item();
            var active = temp[0];
            var next = active.getPrevious() || temp[2][temp[2].length-1];
            var next_index = temp[2].indexOf(next);
            return this.slide('prev', active, next, next_index, cycle);
        },
        'to': function(pos, cycle){
            var thisobj = this;
            var temp = this.get_active_item();
            if(pos<0 || pos > (temp[2].length-1)) return;
            if(temp[1]==pos){
                return;
            }
            var active = temp[0];
            var next = temp[2][pos];
            var next_index = temp[2].indexOf(next);
            this.pause();
            return this.slide(pos > temp[1]? 'next' : 'prev', active, next, next_index, cycle);
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
        'slide': function(type, active, next, next_index, cycle){
            // 等待动画完成
            if(!cycle) this.pause();
            if(this.transitioning()){
                return utils.one(this, 'slid', this.slide.pass([type, active, next, next_index, cycle], this));
            }
            var direction = type == 'next' ? 'left' : 'right';
            //var fallback  = type == 'next' ? 'first' : 'last';
            var thisobj = this;
            this.fireEvent('slide', [active, next, direction]);
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
            if(cycle) this.cycle();
        },
        'transition': function(active, next, next_index, callback){
            var thisobj = this;
            active.removeClass('active');
            active.setStyle('display', 'block');
            next.addClass('active');
            next.setStyle('display', 'none');
            this.fx = new Fx.Tween(active, {
                'property': 'opacity',
                'duration': this.options.duration*0.4,
                'onComplete': function(){
                    next.setStyle('display', 'block');
                    active.setStyle('display', 'none');
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
            carousel[this.get('data-slide')]();
        }
    });    

    return Carousel;
});
