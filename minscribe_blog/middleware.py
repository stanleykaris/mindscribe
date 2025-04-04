from django.conf import settings
from django.db import connection
from django.utils import timezone
import logging
import time

logger = logging.getLogger(__name__)

class ModelChangeLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.
        start_time = timezone.now()
        
        if settings.DEBUG:
            connection.queries = []
        
        response = self.get_response(request)
        
        # Code to be executed for each request/response after
        # the view is called.
        if len(connection.queries) > 0:
            total_time = time.time() - start_time.total_seconds()
            logger.info(f"Request: {request.path} - DB Queries: {len(connection.queries)} - Time: {total_time}s")
            
        return response
