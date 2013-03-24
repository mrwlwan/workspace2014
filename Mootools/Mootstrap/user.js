require.config({
    baseUrl: './',
    paths: {mootstrap: 'js'}
});


require(['mootstrap/Dropdown', 'mootstrap/Collapse', 'mootstrap/Alert', 'mootstrap/Button', 'mootstrap/Tab', 'mootstrap/Affix', 'mootstrap/ScrollSpy', 'mootstrap/Modal', 'mootstrap/Tooltip', 'mootstrap/Popover', 'mootstrap/Typeahead', 'mootstrap/Carousel', 'domReady!'], function(Dropdown, Collapse, Alert, Button, Tab, Affix, ScrollSpy, Modal, Tooltip, Popover, Typeahead, Carousel){
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

    //new Carousel($('myCarousel'));
});
