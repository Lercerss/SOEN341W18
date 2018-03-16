__author__ = 'jet'
import datetime
from haystack import indexes
from qa_web.models import Questions


class QuestionsIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    author = indexes.CharField(model_attr='owner')
    pub_date = indexes.DateTimeField(model_attr='creation_date')

    def get_model(self):
        return Questions

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.filter(pub_date__lte=datetime.datetime.now())