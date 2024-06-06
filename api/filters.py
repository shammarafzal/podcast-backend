# from rest_framework import filters
from django_filters import rest_framework as rest_filter
from .models import *


class EpisodeFilter(rest_filter.FilterSet):
    class Meta:
        
        model = EpisodeModel # the model which it will be associated with
        
        # assigned additional llokup filter fields to the Model field to able to search data easily
        fields = {
            'id': ['exact'],
            'title': ['exact'],
        }
    
        