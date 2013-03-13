/* BUTTON CLASS DEFINITION */
define(['./utils.js'], function(utils){
    var Button = new Class({
        Implements: Options,
        options: {
            'loadingText': 'Loading...'
        },
        'initialize': function(el, options){
            this.el = $(el);
            this.setOptions(options);
        },
        'toElement': function(){
            return this.el;
        },
        '_add_events': function(){
            var thisobj = this;
        },
        'disable': function(){
            this.el.addClass('disabled');
            this.el.set('disabled', 'disabled');
        },
        'enable': function(){
            this.el.removeClass('disabled');
            this.el.erase('disabled');
        },
        'set_state': function(state, disabled){
            var d = 'disabled';
            var val = this.el.match('input') ? 'value' : 'html';
            this.el.retrieve('resetText') || this.el.store('resetText', this.el.get(val));
            this.el.set(val, state=='reset' ? this.el.retrieve('resetText') : (this.options[state+'Text'] || this.get('data-'+state+'-text')));
            if(disabled || state=='loading'){
                this.disable();
            }else{
                this.enable();
            }
        },
        'toggle': function(){
            var container = this.el.getParent('[data-toggle=buttons-radio]');
            if(container){
                container.getElements('.active').removeClass('active');
            }
            this.el.toggleClass('active');
        }
    });

    $$('body').addEvent('click:relay([data-toggle^=button])', function(e){
        var btn = $(e.target);
        if(!btn.hasClass('btn')) btn=btn.getParent('.btn');
        var button = btn.retrieve('button');
        if(!button){
            button = new Button(btn);
            btn.store('button', button)
        }
        button.toggle();
    });

    return Button;
});
