__author__ = 'jet'
from django.utils import timezone
from haystack import indexes
from qa_web.models import Questions


class QuestionsIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True, template_name='search/indexes/qa_web/questions_text.txt')
    owner = indexes.CharField(model_attr='owner')
    creation_date = indexes.DateTimeField(model_attr='creation_date')

    def get_model(self):
        return Questions

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.filter(creation_date__lte=timezone.now())