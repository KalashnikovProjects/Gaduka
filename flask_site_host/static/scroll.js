$.scrollFlag = false;
a = $('.index-section');
var  sectionHeight = a.outerHeight(true) - $("header").height() / 4;


$(window).resize(function(){
    a = $('.index-section');
    sectionHeight = a.outerHeight(true) - $("header").height() / 4;
});


document.addEventListener('wheel', function(e){
    e.preventDefault();
    if ($.scrollFlag) {
        return
    }
    setTimeout(function(){
        $.scrollFlag = false
    }, 1250);

    $.scrollFlag = true
        if(e.deltaY / 120 > 0) {
            $("html,body").animate({ scrollTop: `+=${sectionHeight}px` }, 500, "easeInOutSine",
                function() {
                });
         }
        else{
            $("html,body").animate({ scrollTop: `-=${sectionHeight}px` }, 500, "easeInOutSine",
                function() {
                });}
}, { passive: false })
