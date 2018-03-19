__author__ = 'jet'
# import datetime  # RuntimeWarning: naive datetime is not the best time marker in django
from django.utils import timezone
from haystack import indexes
from qa_web.models import Questions

# If it's the first time you try to use search, please execute: python manage.py rebuild_index
# The search index is configured to be automatically updated once a model instance is saved or deleted that
# has an associated SearchIndex.

class QuestionsIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    owner = indexes.CharField(model_attr='owner')
    creation_date = indexes.DateTimeField(model_attr='creation_date')

    def get_model(self):
        return Questions

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.filter(creation_date__lte=timezone.now())