/*JAVASCRIPT for QA_Web*/

/*Function that populates all the necessary divs with markdown, using markdown-it library
This is only proper to answerspage.html for now
*/
function prepareMarkdown() {
    var md = window.markdownit();

    $(".marked").each(function () {
        var textToMark = $(this).text();
        var result = md.render(textToMark);
        $(this).html(result);
        $(this).find("p").css("margin-bottom", 0);
    });
}


// Callback for voting, sends ajax request to server 
// then updates the corresponding score.
function voteCallback(event) {
    var voteButton = event.currentTarget;
    $.ajax({
        url: '/vote/',
        method: "POST",
        data: {
            'button': voteButton.id,
        },
        dataType: 'json',
        success: function (data) {
            $('#' + data.id).text(data.new_score);
        }
    });
}

// When somebody wants to answer or comment, modify modal settings 
// depending on whether the user is posting an answer or to a comment.
function postReply(event) {
    var commentButton = event.currentTarget;
    var formId;
    var contentId;
    var modalTitle;
    var modalContent;

    // commentButton.id in following format: post(A|C(answer_{id}|question))
    // 5th character decides answer or comment
    // Following differentiate comment on answers from comment on question
    var replyType = commentButton.id.slice(4); 
    modalTitle = $("#title_question").html();

    // Clear textbox and preview contents
    $("#wmd-input").val("");  
    $("#wmd-preview").html("");

    if (replyType[0] == "A") {
        formId = "answer_form";
        modalContent = $("#content_question").html();
        $("#modalTitle").html("Posting Answer");
        $("#postTitle").html("<h3>" + modalTitle + "</h3>");
        $("#postContent").html(modalContent);
    } else {
        formId = "comment_form_";
        contentId = "content_";
        var commentType = replyType.slice(1);
        formId += commentType;
        contentId += commentType;
        modalContent = $("#" + contentId).html();
        $("#modalTitle").html("Posting Comment");
        if (commentType == "question") {
            $("#postTitle").html("<h3>" + modalTitle + "</h3>");
        } else {
            $("#postTitle").html("");
        }
        $("#postContent").html(modalContent);
    }
    $('#submitForm').attr('name', formId);
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

$(document).ready(function () {
    // Displays text in answers pages as MD
    prepareMarkdown();

    var converter = Markdown.getSanitizingConverter();
    var editor = new Markdown.Editor(converter);
    editor.run();

    // Add CSRF Token to ajax requests using POST
    var csrftoken = getCookie('csrftoken');
    $.ajaxSetup({
        beforeSend: function (xhr, settings) {
            if (settings.type == "POST" && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });

    // Get all voting buttons on page
    var voteButtons = $('a').filter(function () {
        return this.id.match(/(up|down)vote_\d+/);
    });

    var postButtons = $('button').filter(function () {
        return this.id.match(/^post/);
    });

    // Register click listeners for voting buttons
    for (let i = 0; i < voteButtons.length; i++) {
        voteButtons[i].onclick = voteCallback;
    }

    for (let i = 0; i < postButtons.length; i++) {
        postButtons[i].onclick = postReply;
    }
});

