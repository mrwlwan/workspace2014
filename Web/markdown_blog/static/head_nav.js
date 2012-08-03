window.addEvent('domready', function(){
    $$('#head_nav .search-query').each(function($el){
        $el.set('tween', {duratoin: 'short'});
        $el.store('orgi_width', $el.getStyle('width').toInt());
        $el.addEvents({
            focus: function(e){
                var $target = $(e.target);
                $target.tween('width', $target.retrieve('orgi_width')*2);
            },
            blur: function(e){
                var $target = $(e.target);
                $target.tween('width', $target.retrieve('orgi_width'));
            }
        });
    });
});
