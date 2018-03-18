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

function post_reply(event) {
  var comment_button = event.currentTarget;
  var form_id;
  var reply_type = comment_button.id.slice(4); //4 since character deciding whether it's answer or comment is 5th character.
  if (reply_type[0] == "A") {
    form_id = "answer_form";
    $("#modalTitle").html("Posting Answer");
  }
  else {
    form_id = "comment_form_";
    var comment_type = reply_type.slice(1);    //Data on whether replying to question or answer starts at 6th character. Slice off 5th character.
    form_id += comment_type;
    $("#modalTitle").html("Posting Comment");
  }
  $('#submitForm').attr('name', form_id);
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

  var post_buttons = $('button').filter(function(){
    return this.id.match(/^post/);
  });

  // Register click listeners for voting buttons
  for(let i = 0; i < vote_buttons.length; i++){
    vote_buttons[i].onclick = vote_callback;
  }

  for(let i = 0; i < post_buttons.length; i++){
    post_buttons[i].onclick = post_reply;
  }
});

