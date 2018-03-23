from django import template
from qa_web.models import Answer, Question, Comment, User
register = template.Library()

@register.simple_tag
def get_answer_parent_title(question_id):
    question = Question.objects.get(id = question_id)
    return question.title

@register.simple_tag
def get_comment_question_id(question_id, answer_id):
    if answer_id is None:
        return question_id
    else:
        a = Answer.objects.get(id = answer_id)
        return a.question_id

@register.simple_tag
def get_comment_parent(comment_id):
    c = Comment.objects.get(id = comment_id)
    if c.answer_id is None:
        parent_question = Question.objects.get(id = c.question_id)
        parent_owner = User.objects.get(id = parent_question.owner_id)
        info = parent_owner.username + "'s question"
        return info
    else:
        parent_answer = Answer.objects.get(id=c.answer_id)
        parent_owner = User.objects.get(id=parent_answer.owner_id)
        info = parent_owner.username + "'s answer"
        return info