from rest_framework import generics, status
from rest_framework.utils import humanize_datetime
import datetime


# Creating a Response Structure for all API responses
class ApiResponseMixin:
    
    RESPONSE_STRUCTURE = {
            "status": None,
            "message": None,
            "data": {},
            "errors": {},
            # "fields": self.queryset.model._meta.get_fields().__str__(),
            # "next": [k for k in response.data.keys()],
            "serverTime": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    
    def structure(self, request, response, errors, *args, **kwargs):
        # response = super().li(self, request, response, *args, **kwargs) 
        
        # checking for errors while going from API Views
        
        # result_data = self.RESPONSE_STRUCTURE.copy()
        self.RESPONSE_STRUCTURE["status"] = response.status_code
        self.RESPONSE_STRUCTURE["message"] = response.status_text
        self.RESPONSE_STRUCTURE["data"] = (response.data if len(errors) == 0 else [])
        self.RESPONSE_STRUCTURE["errors"] = (errors if len(errors) > 0 else [])
        
        response.data = self.RESPONSE_STRUCTURE

        return response