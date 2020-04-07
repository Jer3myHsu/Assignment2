// Code from https://stackoverflow.com/questions/3860629/show-hide-content-depending-if-a-checkbox-is-checked
$(document).ready(function(){
$('.role').hide();
$('.container input').change(function() {
    changeCheck(this);
});

function changeCheck(x) {
    if ($('.container input').is(':checked')) { // I'm not sure about my if here.
        $('.role').fadeIn(200);        // if necessary try exchanging the fadeOut() and fadeIn()
    }
    else {
        $('.role').fadeOut(200);
    }
}
});