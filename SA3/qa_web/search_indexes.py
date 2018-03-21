"""Search Indexes are used to define which Models are indexed and how to handle
data flow for indexing."""
from django.utils import timezone
from haystack import indexes
from qa_web.models import Question


class QuestionsIndex(indexes.SearchIndex, indexes.Indexable):
    """SearchIndex for Questions, defines the necessary relations for 
    haystack's indexing."""
    text = indexes.CharField(document=True, use_template=True,
                    template_name='search/indexes/qa_web/questions_text.txt')
    owner = indexes.CharField(model_attr='owner')
    creation_date = indexes.DateTimeField(model_attr='creation_date')

    def get_model(self):
        return Question

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.filter(
            creation_date__lte=timezone.now())
