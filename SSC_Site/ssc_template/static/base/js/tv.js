function set_screen_sizes() {
	$(".ssc.tv.box").height($(".ssc.tv.box").width()*9/16/2)
	$(".ssc.tv.screen").height($(".ssc.tv.screen").width()*9/16)
}

function set_screen_images() {
	$('.ssc.tv.screen.uni').css('background-image', 'url(' + "'/static/base/image/tv-coming-soon.jpg'" + ')');
	$('.ssc.tv.screen.our').css('background-image', 'url(' + "'/static/base/image/tv-coming-soon.jpg'" + ')');
}

$(window).on('resize', function(){
	set_screen_sizes();
});

$(document).ready(function() {
	set_screen_sizes();
	set_screen_images();
});