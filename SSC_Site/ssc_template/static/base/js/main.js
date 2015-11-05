$(document).ready(function() {

	$('.parallax').parallax();

    $('.dropdown-button').dropdown({
        inDuration: 300,
        outDuration: 225,
        constrain_width: false,
        hover: true,
        gutter: -25,
        belowOrigin: true,
        alignment: 'left'
    });

    $(".button-collapse.rtl").sideNav({
        menuWidth: 300,
        edge: 'right'
    });

    $(".button-collapse.ltr").sideNav({
        menuWidth: 300,
        edge: 'left'
    });

    $('.tooltipped').tooltip({delay: 50});
	
});


