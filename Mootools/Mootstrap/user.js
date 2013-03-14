require(['js/Dropdown', 'js/Collapse', 'js/Alert', 'js/Button', 'js/Tab', 'js/Affix', 'js/ScrollSpy', 'domReady!'], function(Dropdown, Collapse, Alert, Button, Tab, Affix, ScrollSpy){
    $$('.bs-docs-sidenav').each(function(el){
        new Affix(el, {
            'offset': {
                'top': 40,
                'bottom': 200,
            }
        });
    });
});
