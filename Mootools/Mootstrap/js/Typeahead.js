/* TYPEAHEAD CLASS DEFINITION */
define(['./utils.js', './more/Elements_from.js'], function(utils){
    var Typeahead = new Class({
        Implements: [Options, Events],
        options: {
            'source': [],
            'items': 8, // 显示最大数目
            'menu': '<ul class="typeahead dropdown-menu"></ul>',
            'item': '<li><a href="#"></a></li>',
            'minLength': 1, // 最少输入字符数
            'container': null
        },
        'initialize': function(el, options){
            this.el = el;
            this.setOptions(options);
            this.menu = Elements.from(this.options.menu)[0];
            this._inject_menu(this.menu);
            this.el.grab(this.menu, 'after');
            this.shown = false;
            this.focused = false;
            this.mousedover = false;
            if(!this.el.retrieve('typeahead')){
                this._add_events();
                this.el.store('typeahead', this);
            }
        },
        'toElement': function(){
            return this.el;
        },
        '_add_events': function(){
            var thisobj = this;
            this.el.addEvents({
                'focus': this._focus.bind(this),
                'blur': this._blur.bind(this),
                //'keypress', this._keypress.bind(this),
                'keyup': this._keyup.bind(this),
                'keydown': this._keydown.bind(this)
            });
            this.menu.addEvents({
                'click': this._click.bind(this),
                'mouseenter:relay(li)': this._mouseenter.bind(this),
                'mouseleave:relay(li)': this._mouseleave.bind(this)
            });
        },
        '_inject_menu': function(menu){
            if(this.options.container){
                menu.inject(this.options.container);
            }else{
                menu.inject(this.el, 'after');
            }
            return menu;
        },
        'select': function(val){
            val = val!=undefined ? val : this.menu.getElement('.active').get('data-value');
            this.el.set('value', this.updater(val))
                .fireEvent('change');
            return this.hide();
        },
        'updater': function(val){
            if(this.options.updater){
                return this.options.updater(val);
            }else{
                return val;
            }
        },
        'hide': function(){
            if(this.shown){
                this.menu.setStyle('display', 'none');
                this.shown = false;
            }
            return this;
        },
        'show': function(){
            if(!this.shown){
                var el_coordinate = this.el.getCoordinates(this.options.container || this.el.getOffsetParent() || document.body);
                this.menu.setStyles({
                    'top': el_coordinate.top+el_coordinate.height,
                    'left': el_coordinate.left,
                    'display': 'block'
                });
                this.shown = true
            }
            return this;
        },
        'load_source': function(url){
            new Request.JSON({
                'url': url,
                'async': false,
                'onSucess': function(source){
                    return source;
                }
            });
        },
        'get_source': function(){
            var items;
            switch(typeOf(this.options.source)){
                case 'function':
                    items = this.process(this.options.source(query));
                    break;
                case 'string':
                    this.options.source = this.load_source(this.options.source.replace('{query}', query));
                case 'array':
                    items = this.options.source;
            }
            return items;
        },
        'lookup': function(){
            var query = this.el.get('value');
            if(!query || query.length < this.options.minLength){
                //return this.shown ? this.hide() : this;
                return this.hide();
            }
            var items = this.get_source();
            return items ? this.process(items, query) : this;
        },
        'process': function(items, query){
            var thisobj = this;
            items = items.filter(function(item){
                return thisobj.matcher(item, query);
            });
            items = this.sorter(items, query);
            if(!items.length){
                //return this.shown ? this.hide() : this;
                return this.hide();
            };
            return this.render(items.slice(0, this.options.items), query).show();
        },
        'matcher': function(item, query){
            if(this.options.matcher){
                return this.options.matcher(item, query);
            }
            return item.toLowerCase().indexOf(query.toLowerCase()) >= 0;
        },
        'sorter': function(items, query){
            if(this.options.sorter){
                return this.options.sorter(item, query);
            }
            var beginswith = [];
            var caseSensitive = [];
            var caseInsensitive = [];
            var item;
            while(item = items.shift()){
                if(!item.toLowerCase().indexOf(query.toLowerCase())) beginswith.push(item)
            else if (~item.indexOf(query)) caseSensitive.push(item)
            else caseInsensitive.push(item)
          }
          return beginswith.concat(caseSensitive, caseInsensitive)
        },
        'highlighter': function(item, query){
            if(this.options.sorter){
                return this.options.highlighter(item, query);
            }
            query = query.replace(/[\-\[\]{}()*+?.,\\\^$|#\s]/g, '\\$&');
            return item.replace(new RegExp('(' + query + ')', 'ig'), function($1, match){
                return '<strong>' + match + '</strong>';
            });
        }, 
        'render': function(items, query){
            var thisobj = this;
            this.menu.empty();
            items.each(function(item, index){
                var i = Elements.from(thisobj.options.item)[0];
                if(index==0) i.addClass('active');
                i.set('data-value', item);
                i.getElement('a').set('html', thisobj.highlighter(item, query));
                i.inject(thisobj.menu)
            });
            return this;
        },
        'next': function(){
            var active = this.menu.getElement('.active');
            active.removeClass('active');
            var next = active.getNext();
            if(!next){
                next = this.menu.getElement('li')[0];
            }
            next.addClass('active')
            return next;
        },
        'prev': function(){
            var active = this.menu.getElement('.active');
            active.removeClass('active');
            var previous = active.getPrevious();
            if(!previous){
                previous = this.menu.getElement('li').getLast();
            }
            previous.addClass('active')
            return previous;
        },
        // 键盘十字键上下移动
        '_move': function(e){
            if(!this.shown) return;
            switch(e.code) {
                case 9: // tab
                case 13: // enter
                case 27: // escape
                    e.preventDefault();
                    break;
                case 38: // up arrow
                    e.preventDefault();
                    this.prev();
                    break;
                case 40: // down arrow
                    e.preventDefault();
                    this.next();
                    break;
            }
            e.stopPropagation();
        },
        '_keydown': function(e){
      //this.suppressKeyPressRepeat = ~$.inArray(e.keyCode, [40,38,9,13,27])
            this._move(e);
        },
        //'keypress': function(e){
            //this.move(e)
        //},
        '_keyup': function(e){
            switch(e.code) {
                case 40: // down arrow
                case 38: // up arrow
                case 16: // shift
                case 17: // ctrl
                case 18: // alt
                    break
                case 9: // tab
                case 13: // enter
                  if (!this.shown) return;
                  this.select();
                  break;
                case 27: // escape
                  if (!this.shown) return;
                  this.hide();
                  break;
                default:
                  this.lookup();
            }
            e.stopPropagation();
            e.preventDefault();
        },
        '_focus': function(e){
            e.stop();
            this.focused = true;
            return false;
        },
        '_blur': function(e){
            this.focused = false;
            if (!this.mousedover && this.shown) this.hide();
        },
        '_click': function(e, target){
            e.stopPropagation();
            e.preventDefault();
            this.select();
            this.focused = true;
        },
        '_mouseenter': function(e, target){
            this.mousedover = true
            this.menu.getElement('.active').removeClass('active');
            target.addClass('active');
        },
        '_mouseleave': function(e, target){
            this.mousedover = false;
            if (!this.focused && this.shown) this.hide();
        }
    });


    $(document.body).addEvent('focus:relay([data-provide=typeahead])', function(e){
        if(this.retrieve('typeahead')) return;
        var options = utils.get_options(this, {'source': 'json', 'items': 'int', 'minLength': 'int'})
        new Typeahead(this, options);
    });

    return Typeahead;
});

