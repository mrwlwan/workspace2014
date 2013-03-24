/* ALERT CLASS DEFINITION */
define(['mootstrap/utils'], function(utils){
    var dismiss = '[data-dismiss=alert]';

    var Alert = new Class({
        Implements: [Options, Events],
        options: {
            'fade': true,
            'duration': 250
        },
        'initialize': function(el, options){
            this.el = $(el);
            this.setOptions(options);
            if(!this.el.retrieve('alert')){
                this._add_events();
                this.el.store('alert', this);
            }
        },
        'toElement': function(){
            return this.get_container();
        },
        '_add_events': function(){
            var thisobj = this;
            this.el.addEvent('click', function(e){
                e.stop();
                document.fireEvent('click');
                thisobj.close(e);
            });
        },
        'get_container': function(){
            return utils.get_targets(this.el)[0] || this.el.getParent();
        },
        'close': function(e){
            var thisobj = this;
            var container = this.get_container();
            this.fireEvent('close');
            if(this.options.fade){
                container.setStyle('opacity', 1);
                new Fx.Tween(container, {
                    'property': 'opacity',
                    'duration': this.options.duration,
                    'onComplete': function(){
                        container.destroy();
                        thisobj.fireEvent('closed');
                    }
                }).start(0);
            }else{
                container.destroy();
                thisobj.fireEvent('closed');
            }
            return false;
        }            
    });

    $$('body').addEvent('click:relay('+dismiss+')', function(e){
        var options = utils.get_options(this, {'fade': 'bool', 'duration': 'int'});
        new Alert(this, options).close(e);
    });

    return Alert;
});
