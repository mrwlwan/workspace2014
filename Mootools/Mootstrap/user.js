require(['js/Dropdown', 'js/Collapse', 'js/Alert', 'js/Button', 'js/Tab', 'domReady!'], function(Dropdown, Collapse, Alert, Button, Tab){
    var btn = $('loading_btn');
    var button = new Button(btn, {'processText': 'process...'});
    btn.addEvent('click', function(e){
        button.set_state('loading');
        button.set_state.delay(1000, button, ['process', true]);
        button.set_state.delay(3000, button, 'reset');
        button.toggle.delay(5000, button);
    });
});
