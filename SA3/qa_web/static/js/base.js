/*JAVASCRIPT for QA_Web*/

$(document).ready(function(){
  var converter = Markdown.getSanitizingConverter();
  var editor = new Markdown.Editor(converter);
  editor.run();
});