/* ALERT CLASS DEFINITION */
define(['./utils.js'], function(utils){
    var dismiss = '[data-dismiss=alert]';

    var Alert = new Class({
        Implements: [Options, Events],
        options: {
            'false': true
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
                thisobj.close(e);
                document.fireEvent('click');
            });
        },
        'get_container': function(){
            return utils.get_targets(this.el)[0] || this.el.getParent();
        },
        'close': function(e){
            var container = this.get_container();
            this.fireEvent('close');
            this.options.fade && container.fade('out');
            container.destroy();
            this.fireEvent('closed');
            return false;
        }            
    });

    $$('body').addEvent('click:relay('+dismiss+')', function(e){
        var options = utils.get_options(this, {'fade': 'bool'});
        new Alert(this, options).close(e);
    });

    return Alert;
});
