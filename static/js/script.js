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
$('.chips-placeholder-1').chips({
    placeholder: 'Genre',
    secondaryPlaceholder: 'Add Another',
});

// PLACEHOLDER FOR TAGS
$('.chips-placeholder-2').chips({
    placeholder: 'Tags',
    secondaryPlaceholder: 'Add Another',
});

// AUTOCOMPLETE FOR GENRE
$('.chips-autocomplete-1').chips({
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

// AUTOCOMPLETE FOR TAGS
$('.chips-autocomplete-2').chips({
    autocompleteOptions: {
        data: {
            'Emotional': null,
            'Poignant': null,
            'Surreal': null
        },
        limit: Infinity,
        minLength: 1
    }
  });