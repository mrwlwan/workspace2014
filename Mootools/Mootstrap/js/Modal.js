/* MODAL CLASS DEFINITION */
define(['mootstrap/utils', 'mootstrap/more/DragMove'], function(utils, DragMove){
    var Modal = new Class({
        Implements: [Options, Events],
        options: {
            'remote': null,
            'draggable': true,
            'fade': false,
            'backdrop': true,
            'transition': true,
            'duration': 300,
            'keyboard': true,
        },
        'initialize': function(el, options){
            this.el = $(el);
            this.header = this.el.getElement('.modal-header');
            this.body = this.el.getElement('.modal-body');
            this.footer = this.el.getElement('.modal-footer');
            this.header = this.el.getElement('.modal-header');
            this.backdrop = null;
            this.draggable = null;
            this.setOptions(options);
            this.options.remote && this.load(this.options.remote);
            if(!this.el.retrieve('modal')){
                this._add_events();
                this.el.store('modal', this);
            }
        },
        'toElement': function(){
            return this.el;
        },
        '_add_events': function(){
            var thisobj = this;
            this.el.addEvent('click:relay([data-dismiss=modal])', this.hide.bind(this));
            this.options.keyboard && this.el.addEvent('keyup', function(e){
                e.code == 27 && thisobj.hide();
            });
        },
        // 加载异步内容
        'load': function(url, callback){
            var thisobj = this;
            return new Request({
                'url': url,
                'method': 'get',
                'onSuccess': function(text){
                    thisobj.empty();
                    thisobj.set('html', text);
                    callback && callback();
                }
            }).send();                    
        },
        'clear': function(){
            this.body.empty();
        },
        'set_title': function(title, selector){
            var success = false;
            this.header.getElements().each(function(item){
                if((selector && item.match(selector)) || /h\d+/.test(item.get('tag'))){
                    item.set('html', title);
                    success = true;
                }
            });
            success || this.header.set('html', title);
        },
        'is_fade': function(){
            return this.options.fade || this.el.hasClass('fade');
        },
        'is_shown': function(){
            return utils.is_visible(this.el);
        },
        'toggle': function(){
            return this[!this.is_shown() ? 'show' : 'hide']();
        },
        'create_backdrop': function(){
            this.backdrop = utils.back_drop(document.body, {'callback': this.hide.bind(this)});
            return this.backdrop;
        },
        'remove_backdrop': function(){
            this.backdrop && this.backdrop.destroy();
        },
        'transition': function(reverse, callback){
            var coordinates = this.el.getCoordinates();
            var top_array = [-coordinates.height, coordinates.top];
            var opacity_array = [0, 1];
            new Fx.Morph(this.el, {
                'duration': this.options.duration,
                'onComplete': function(){callback && callback();}
            }).start({
                'top': reverse ? top_array.reverse() : top_array,
                'opacity': reverse ? opacity_array.reverse() : opacity_array
            });
        },
        'show': function(){
            var thisobj = this;
            if(this.is_shown()) return;
            if(this.options.draggable){
                if(!this.draggable){
                    this.draggable = new DragMove(this.el, {
                        'handle': this.header
                    });
                    this.header.setStyle('cursor', 'move');
                }
                this.el.setStyle('top', '').setStyle('left', '');
            }
            // Show事件触发.
            this.fireEvent('show');

            this.options.backdrop && this.create_backdrop();
            this.options.transition && this.el.setStyle('opacity', 0);
            this.el.addClass('in').setStyle('display', 'block');
            this.options.transition && this.transition();
            this.el.focus();// for esc key press event
            // Shown事件触发
            this.fireEvent.delay(this.options.duration, this, 'shown');
        },
        '_hide': function(){
            this.el.removeClass('in').setStyle('display', 'none');
            this.remove_backdrop();
        },
        'hide': function(){
            if(!this.is_shown()) return;
            // hidden 事件触发
            this.fireEvent('hide');
            if(this.options.transition){
                this.el.setStyle('opacity', 1);
                this.transition(true, this._hide.bind(this));
            }else{
                this._hide();
            }
            // hidden 事件触发
            this.fireEvent.delay(this.options.duration, this, 'hidden');
        }
    });

    document.body.addEvent('click:relay([data-toggle=modal])', function(e){
        e.preventDefault();
        var modal = this.retrieve('modal');
        if(!modal){
            var target = utils.get_targets(this)[0];
            var options = utils.get_options({'fade': 'bool', 'transition': 'bool', 'duration': 'int', 'draggable': 'bool', 'remote': 'string', 'backdrop': 'bool', 'keyboard': 'bool'});
            modal = new Modal(target);
            this.store('modal', modal);
        }
        modal.toggle();
    });

    return Modal;
});
