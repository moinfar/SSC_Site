$(document).ready(function() {

	$('.parallax').parallax();

    $('.dropdown-button').dropdown({
        inDuration: 300,
        outDuration: 225,
        constrainWidth: false,
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

function intcomma(nStr) {
    nStr += '';
    var x = nStr.split('.');
    var x1 = x[0];
    var x2 = x.length > 1 ? '.' + x[1] : '';
    var rgx = /(\d+)(\d{3})/;
    while (rgx.test(x1)) {
        x1 = x1.replace(rgx, '$1' + ',' + '$2');
    }
    return x1 + x2;
}



