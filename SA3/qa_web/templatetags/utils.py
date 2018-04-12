"""
Template tags that allow for quick backend operation calls
from the templates
"""

from django import template
from qa_web.models import Answer, Question, Comment, User
register = template.Library()

@register.simple_tag
def get_answer_parent_title(question_id):
    """
    Method that obtains a question's title
    :param question_id: question' unique id
    :return: Question title in string
    """
    question = Question.objects.get(id=question_id)
    return question.title

@register.simple_tag
def get_comment_question_id(question_id, answer_id):
    """
    Method that obtains a comment's question id or answer on
    user profile page
    :param question_id: Possible question id
    :param answer_id: Possible answer id
    :return: if comment to question, return that question id
    else if comment to answer, return answer's comment id
    """
    if answer_id is None:
        return question_id
    else:
        answer = Answer.objects.get(id=answer_id)
        return answer.question_id

@register.simple_tag
def get_comment_parent(comment_id):
    """
    Method that obtains part of the message to be displayed below a comment
    on the user profile page
    :param comment_id: comment's unique id
    :return: String indicating who's question or answer it was
    """
    comment = Comment.objects.get(id=comment_id)
    if comment.answer_id is None:
        parent_question = Question.objects.get(id=comment.question_id)
        parent_owner = User.objects.get(id=parent_question.owner_id)
        info = parent_owner.username + "'s question"
        return info
    else:
        parent_answer = Answer.objects.get(id=comment.answer_id)
        parent_owner = User.objects.get(id=parent_answer.owner_id)
        info = parent_owner.username + "'s answer"
        return info
