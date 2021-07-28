// SIDENAV COLLAPSE
$(document).ready(function(){
    $('.sidenav').sidenav({edge: "right"});
});


// ENABLE TEXT AREA IN FORMS
$('#textarea1').val('New Text');
    M.textareaAutoResize($('#textarea1'));

