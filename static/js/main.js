// AOS.init({
//     duration:1000
// });

// $(window).on("load", function () {
// 	AOS.refresh();
// });
// $(".Top-Content").on('scroll', function () {
//     AOS.refresh();
//     alert("scroll")
    
// });

AOS.init({
    duration:1500
});
window.addEventListener('load', AOS.refresh);

let controller = new ScrollMagic.Controller();
let timeline  = new TimelineMax();

timeline
.to(".Top-Content",2,{opacity:0.5})
.to (".navbar",2,{opacity:0.5},'-=2')
.to(".second-top",3,{top: '0%',opacity:1},'-=1.2')

let scene  = new ScrollMagic.Scene({
    triggerElement:".Top-Content",
    duration:"100%",
    triggerHook:0,
})
.setTween(timeline)
.setPin(".Top-Content")
.addTo(controller)
.on("update",function(e){
    AOS.refresh()
})

// let scroller =  new ScrollMagic.Controller();
// let timeline1 = new TimelineMax();

// timeline1
// .fromTo(".card", 1, {left:-100}, {left:0, opacity:1});

// let scene2  = new ScrollMagic.Scene({
//     triggerElement:".card-container",
//     duration:"10%",
//     triggerHook:0,
// })
// .setTween(timeline1)
// .setPin(".card-container")
// .addTo(scroller)
