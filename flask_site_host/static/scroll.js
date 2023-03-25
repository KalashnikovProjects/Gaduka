var scrollFlag = false;
a = $('.index-section');
var  sectionHeight = a.outerHeight(true);


$(window).resize(function(){
    a = $('.index-section');
    sectionHeight = a.outerHeight(true);
});


document.addEventListener('wheel', function(e){
    e.preventDefault();
    if (scrollFlag) {
        return
    }
    scrollFlag = true
    if(e.deltaY / 120 > 0) {
        $.smoothScroll({afterScroll: function() { scrollFlag = false}}, `+=${sectionHeight}px`)
    }
    else{
        $.smoothScroll({afterScroll: function() { scrollFlag = false}}, `-=${sectionHeight}px`)
    }
}, { passive: false })