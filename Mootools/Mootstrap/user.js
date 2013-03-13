require(['js/Dropdown', 'js/Collapse', 'js/Alert', 'js/Button', 'js/Tab', 'js/Affix', 'domReady!'], function(Dropdown, Collapse, Alert, Button, Tab, Affix){
    $$('.bs-docs-sidenav').each(function(el){
        new Affix(el, {
            'offset': {
                'top': function(){return window.getSize().y <= 980 ? 290 : 210},
                'bottom': 270
            }
        });
    });
});
