/* COLLAPSE CLASS DEFINITION 
 * 使用Mootools内置的accordion特效.
 * */
define(['./utils.js', './fx/FxAccordion.js'], function(utils, FxAccordion){
    // 事件处理函数
    var Collapse = new Class({
        Extends: FxAccordion,
        options: {
            'opacity': false,
            'alwaysHide': true,
            'initialDisplayFx': false,
            'resetHeight': false
        },
        'initialize': function(el, options){
            this.el = $(el);
            if(options && options.parent){
                this.container = $(options.parent);
            }else{
                this.container = $$(this.el.get('data-parent'))[0];
                if(!this.container) this.container = this.el.getParent('.accordion');
            }
            this.parent(
                this.container.getElements('.accordion-heading'),
                this.container.getElements('.accordion-body'),
                options
            );
        }
    });

    // 事件处理函数
    function create_collapse(e){
        var collapse = new Collapse(this);
        $body.removeEvent('click:relay([data-toggle=collapse])', create_collapse);
    }
        
    var $body = $$('body');
    $body.addEvent('click:relay([data-toggle=collapse])', create_collapse);

    return Collapse;
})
