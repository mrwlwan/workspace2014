require(['js/Dropdown', 'js/Collapse', 'js/Alert', 'js/Button', 'js/Tab', 'js/Affix', 'js/ScrollSpy', 'js/Modal', 'js/Tooltip', 'js/Popover', 'js/Typeahead', 'domReady!'], function(Dropdown, Collapse, Alert, Button, Tab, Affix, ScrollSpy, Modal, Tooltip, Popover, Typeahead){
    $$('.bs-docs-sidenav').each(function(el){
        new Affix(el, {
            'offset': {
                'top': 40,
                'bottom': 200,
            }
        });
    });
    $$('.tooltip-demo').each(function(item){
        new Tooltip(item, {
            'selector': 'a[data-toggle=tooltip]',
            'placement': function(el){
                return el.get('data-placement') || 'top';
            }
        });
    });

    $$('.tooltip-test').each(function(item){
        new Tooltip(item, {
            //'container': $$('#myModal .modal-body')[0]
        });
    });

    //$$('.popover-test').each(function(item){
        //new Popover(item, {
            //'container': item.getParent()
        //});
    //});

    $$('a[data-toggle=popover]').each(function(item){
        new Popover(item, {
            'container': item.getParent('.bs-docs-example'),
            'placement': function(el){
                return el.get('data-placement') || 'right';
            }
        });
    });
});
