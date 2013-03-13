/* TAB CLASS DEFINITION */
define(['./utils.js'], function(utils){
    var Tab = new Class({
        Implements: [Options, Events],
        options: {
            'fade': false
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
        'transition': function(hide_content, show_content){
            var thisobj = this;
            [{'content': hide_content, 'start': 0.6, 'end': 0, 'method': 'removeClass'},
             {'content': show_content, 'start': 0, 'end': 1, 'method': 'addClass'}
            ].each(function(item){
                if(thisobj.options.fade || item.content.hasClass('fade')){
                    item.content.setStyle('opacity', item.start);
                    var tween = new Fx.Tween(item.content, {
                        'property': 'opacity',
                        'duration': 'short',
                        'onComplete': function(){
                            item.content[item.method]('in')[item.method]('active');
                        }
                    });
                    tween.start(item.end);
                }else{
                    item.content[item.method]('in')[item.method]('active');
                }
            });
        },                    
        'active': function(tab){
            var active_tab = this.get_active_tab();
            // show事件触发
            this.fireEvent('show', tab, active_tab);
            this._get_tab_wraps(active_tab).removeClass('active');
            this._get_tab_wraps(tab).addClass('active');
            var hide_content = this.get_content(active_tab);
            var show_content = this.get_content(tab);
            this.transition(hide_content, show_content);
            this.fireEvent.delay(250, this, ['shown', tab, active_tab]);
        },
        'show': function(tab){
            if(this.is_active(tab)) return;
            this.active(tab);
        }
    });

    $$('body').addEvent('click:relay([data-toggle=tab])', function(e){
        e.preventDefault();
        new Tab(this.getParent('.nav-tabs')).show(this);
    });

    return Tab;
});
