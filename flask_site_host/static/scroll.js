$.scrollFlag = false;
a = $('.index-section');
var  sectionHeight = a.outerHeight(true) - $("header").height() / 4;


$(window).resize(function(){
    a = $('.index-section');
    sectionHeight = a.outerHeight(true) - $("header").height() / 4;
});


document.addEventListener('wheel', function(e){
    e.preventDefault();
    console.log($.scrollFlag);
    if ($.scrollFlag) {
        return
    }
    $.scrollFlag = true
    try {
        if(e.deltaY / 120 > 0) {
            $("html").animate({ scrollTop: `+=${sectionHeight}px` }, 500, "easeInOutSine");
         }
        else{
            $("html").animate({ scrollTop: `-=${sectionHeight}px` }, 500, "easeInOutSine");}
         setTimeout(function(){
            $.scrollFlag = false
            }, 750);

    } catch (err) {
        setTimeout(function(){
        $.scrollFlag = false
        }, 1000);
        if(e.deltaY / 120 > 0) {
            $("html").animate({ scrollTop: `+=${sectionHeight}px` });
        }
        else{
            $("html").animate({ scrollTop: `-=${sectionHeight}px` });}

    }
}, { passive: false })