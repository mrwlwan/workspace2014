$(function(){
    $('#head_nav .search-query').on('focus', function(e){
        var $target = $(e.target);
        $target.animate({
            width: '12em',
        }, 'fast');
    }).on('blur', function(e){
        var $target = $(e.target);
        $target.animate({
            width: '6em',
        }, 'fast');
    });
});

