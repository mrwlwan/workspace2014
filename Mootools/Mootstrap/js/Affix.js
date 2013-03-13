/* AFFIX CLASS DEFINITION */
define(['./utils.js'], function(utils){
    var Affix = new Class({
        Implements: Options,
        options: {
            //'offset': {'top': 0, 'bottom': 0}
            'offset': 0
        },
        'initialize': function(el, options){
            this.el = $(el);
            this.setOptions(options);
            if(!this.el.retrieve('affix')){
                this._add_events();
                this.el.store('affix', this);
            }
            this.check_position();
        },
        'toElement': function(){
            return this.el;
        },
        '_add_events': function(){
            var thisobj = this;
            window.addEvent('scroll', function(e){
                console.log('window scroll form affix');
                thisobj.check_position.attempt([], thisobj);
            });
            //window.addEvent('click', function(e){
                //thisobj.check_position.delay(1, thisobj);
            //});
        },
        'check_position': function(){
            console.log('start check position');
            if(!utils.is_visible(this.el)) return;
            console.log('affix is visible');
            var scroll_height = window.getScrollSize().y;
            var scroll_top = window.getScroll().y;
            var coordinates = this.el.getCoordinates();
            var offset = this.options.offset;
            var offset_bottom = offset.bottom;
            var offset_top = offset.top;
            var reset = 'affix affix-top affix-bottom';
            var affix;

            if(typeOf(offset)!='object') offset_bottom = offset_top = offset;
            if(typeOf(offset_top)=='function') offset_top = offset.top();
            if(typeOf(offset_bottom)=='function') offset_bottom = offset.bottom();

            console.log(offset_bottom);
            console.log(coordinates.top);
            console.log(coordinates.height);
            console.log(scroll_height);
            console.log(scroll_top);

            if(this.unpin != null && (scroll_top + this.unpin <= coordinates.top)){
                affix = false;
            }else if(offset_bottom != null && (coordinates.top + coordinates.height + (affix!='bottom'?scroll_top:0) >= scroll_height - offset_bottom)){
                affix = 'bottom';
            }else if(offset_top != null && scroll_top <= offset_top){
                affix = 'top';
            }else{
                affix = false;
            }

            if(this.affixed===affix) return;
            this.affixed = affix;
            this.unpin = affix == 'bottom' ? coordinates.top - scroll_top : null;

            console.log(affix);
            utils.remove_classes(this.el, reset).addClass('affix' + (affix ? '-' + affix : ''));
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
