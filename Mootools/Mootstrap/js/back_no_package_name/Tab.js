/* TAB CLASS DEFINITION */
define(['./utils.js'], function(utils){
    var Tab = new Class({
        Implements: [Options, Events],
        options: {
            'fade': false,
            'duration': 250
        },
        'initialize': function(container, options){
            this.container = $(container);
            this.setOptions(options);
            if(!this.container.retrieve('tab')){
                this._add_events();
                this.container.store('tab', this);
            }
        },
        'toElement': function(){
            return this.container;
        },
        '_add_events': function(){
            var thisobj = this;
            this.container.addEvent('click:relay([data-toggle=tab])', function(e){
                e.stop();
                thisobj.show(this);
                thisobj.container.click();
                return false;
            });
        },
        '_get_tab_wraps': function(tab){
            return tab.getParents('li');
        },
        '_get_tab_wrap': function(tab){
            return this._get_tab_wraps(tab)[0];
        },
        'is_active': function(tab){
            return this._get_tab_wrap(tab).hasClass('active');
        },
        'get_active_tab': function(){
              return this.container.getElements('.active').getLast().getElement('a');
        },
        'get_content': function(tab){
            return utils.get_targets(tab)[0];
        },
        'transition': function(content, start, end, method, callback){
            var thisobj = this;
            if(thisobj.options.fade || content.hasClass('fade')){
                content.setStyle('opacity', start);
                end>=1 && content.addClass('in').addClass('active');
                var tween = new Fx.Tween(content, {
                    'property': 'opacity',
                    'duration': thisobj.options.duration/2,
                    'onComplete': function(){
                        content[method]('in')[method]('active');
                        callback && callback();
                    }
                });
                tween.start(end);
            }else{
                content[method]('in')[method]('active');
                callback && callback();
            }
        },                    
        'active': function(tab){
            var active_tab = this.get_active_tab();
            // show事件触发
            this.fireEvent('show', tab, active_tab);
            this._get_tab_wraps(active_tab).removeClass('active');
            this._get_tab_wraps(tab).addClass('active');
            var hide_content = this.get_content(active_tab);
            var show_content = this.get_content(tab);
            this.transition(hide_content, 1, 0.2, 'removeClass', this.transition.pass([show_content, 0.3, 1, 'addClass'], this));
            this.fireEvent.delay(this.options.duration, this, ['shown', tab, active_tab]);
        },
        'show': function(tab){
            if(this.is_active(tab)) return;
            this.active(tab);
        }
    });

    $$('body').addEvent('click:relay([data-toggle=tab])', function(e){
        e.preventDefault();
        var container = this.getParent('.nav-tabs');
        var options = utils.get_options(container, {'duration': 'int', 'fade': 'bool'})
        new Tab(container, options).show(this);
    });

    return Tab;
});
