/*JAVASCRIPT for QA_Web*/

/*Function that populates all the necessary divs with markdown, using markdown-it library
This is only proper to answerspage.html for now
*/
function prepare_markdown(){
    var md = window.markdownit();

    $(".marked").each(function(){
        var textToMark = $(this).text();
        var result = md.render(textToMark);
        $(this).html(result);
        $(this).find("p").css("margin-bottom",0);
    });
}


// Callback for voting, sends ajax request to server then updates the corresponding score
function vote_callback(event){
  var vote_button = event.currentTarget
  $.ajax({
    url: '/vote/',
    method: "POST",
    data: {
      'button' : vote_button.id,
    },
    dataType: 'json',
    success: function(data){
      $('#' + data.id).text(data.new_score);
    }
  });
}

function post_comment(event) {
  switch_comment_view(event);
  $('#'+event.currentTarget.id).hide();
}

function hide_comment(event) {
  switch_comment_view(event);
  $('#postC'+event.currentTarget.id.slice(5)).show();
}

function switch_comment_view(event, buttonToShow) {
  var comment_button = event.currentTarget;
  var form_id = "comment_form_";
  var comment_type = comment_button.id.slice(5); //5 since first five characters are "hideC" or "postC"

  if (comment_type == "Q")
    form_id += ("question");
  else if (comment_type.match(/A/)) {
    var answer_id = comment_type.slice(2); //Slices off A_
    form_id += ("answer_" + answer_id);
  }

  if (comment_button.id.match(/^post/))
    $("#"+form_id).show();
  else if (comment_button.id.match(/^hide/))
    $("#"+form_id).hide();
  $('#postC'+comment_type).show();
}

// From Django docs on CSRF
function getCookie(name) {
  var cookieValue = null;
  if (document.cookie && document.cookie !== '') {
      var cookies = document.cookie.split(';');
      for (var i = 0; i < cookies.length; i++) {
          var cookie = jQuery.trim(cookies[i]);
          if (cookie.substring(0, name.length + 1) === (name + '=')) {
              cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
              break;
          }
      }
  }
  return cookieValue;
}

/*JS to execute as soon as document is ready*/
$(document).ready(function(){

  // Displays text in answers pages as MD
  prepare_markdown();

  var converter = Markdown.getSanitizingConverter();
  var editor = new Markdown.Editor(converter);
  editor.run();

  // Add CSRF Token to ajax requests using POST
  var csrftoken = getCookie('csrftoken')
  $.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (settings.type == "POST" && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
  });

  // Get all voting buttons on page
  var vote_buttons = $('a').filter(function(){
    return this.id.match(/(up|down)vote_\d+/);
  });

  var post_comment_buttons = $('a').filter(function(){
    return this.id.match(/^post/);
  });

  var hide_comment_buttons = $('a').filter(function(){
    return this.id.match(/^hide/);
  });

  var comment_forms = $('form').filter(function(){
    return this.id.match(/^comment_form_/);
  });

  // Register click listeners for voting buttons
  for(let i = 0; i < vote_buttons.length; i++){
    vote_buttons[i].onclick = vote_callback;
  }

  for(let i = 0; i < post_comment_buttons.length; i++){
    post_comment_buttons[i].onclick = post_comment;
  }

  for(let i = 0; i < hide_comment_buttons.length; i++){
    hide_comment_buttons[i].onclick = hide_comment;
  }

  for(let i = 0; i < comment_forms.length; i++){
    id = comment_forms[i].id;
    $("#"+id).hide();
  }
});

