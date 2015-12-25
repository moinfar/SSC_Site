function set_screen_sizes() {
	$(".ssc.tv.box").height($(".ssc.tv.box").width()*9/16/2)
	$(".ssc.tv.screen").height($(".ssc.tv.screen").width()*9/16)
}

function set_screen_images() {
	$('#right-screen-image-slider').show();
	$('#left-screen-image-slider').show();
    $('#right-screen-image-slider').slider({interval: 10000, indicators: false, height: $('#right-screen-image-slider').width()*9/16});
    $('#left-screen-image-slider').slider({interval: 10000, indicators: false, height: $('#left-screen-image-slider').width()*9/16});
}

$(window).on('resize', function(){
	set_screen_sizes();
	//set_screen_images();
});

$(document).ready(function() {
	set_screen_sizes();
	set_screen_images();
});