// SIDENAV COLLAPSE
$(document).ready(function(){
    $('.sidenav').sidenav({edge: "right"});
});

// ADD_FILM > YEAR DATEPICKER
$(document).ready(function(){
    $('.datepicker').datepicker({format: "yyyy"});
});

// ENABLE TEXT AREA IN FORMS
$('#textarea1').val('New Text');
    M.textareaAutoResize($('#textarea1'));

// PLACEHOLDER FOR GENRE
$('.chips-placeholder').chips({
    placeholder: 'Genre',
    secondaryPlaceholder: 'Add Another',
});

// AUTOCOMPLETE FOR GENRE
$('.chips-autocomplete').chips({
    autocompleteOptions: {
        data: {
            'Action': null,
            'Adventure': null,
            'Crime': null
        },
        limit: Infinity,
        minLength: 1
    }
  });