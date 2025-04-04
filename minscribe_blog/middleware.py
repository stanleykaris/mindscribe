from django.db import connection, reset_queries
from django.conf import settings
import logging
from typing import Any, Callable
from django.http import HttpRequest, HttpResponse
import time

logger = logging.getLogger(__name__)

class ModelChangeLoggingMiddleware:
    """
    Middleware to log database queries and execution time for each request.
    """
    
    SLOW_QUERY_THRESHOLD = 1.0  # seconds
    
    def __init__(self, get_response: Callable) -> None:
        self.get_response = get_response
        
    def __call__(self, request: HttpRequest) -> HttpResponse:
        """Process the request and log database activity."""
        # Only track queries in debug mode
        if settings.DEBUG:
            return self._handle_debug_request(request)
        return self.get_response(request)
    
    def _handle_debug_request(self, request: HttpRequest) -> HttpResponse:
        """Handle request with query logging in debug mode."""
        # Clear the query log
        reset_queries()
        
        # Record start time
        start_time = time.time()
        
        # Process the request
        response = self.get_response(request)
        
        # Log database activity
        self._log_database_activity(request, start_time)
        
        return response
    
    def _log_database_activity(self, request: HttpRequest, start_time: float) -> None:
        """Log information about database queries."""
        # Get the query log
        queries = connection.queries
        
        if not queries:
            logger.info(f"No database queries for request: {request.path}")
            return
            
        # Calculate statistics
        total_time = time.time() - start_time
        query_count = len(queries)
        db_time = sum(float(q.get('time', 0)) for q in queries)
        
        # Prepare log data
        log_data = {
            'path': request.path,
            'method': request.method,
            'user': request.user.username if hasattr(request, 'user') and request.user.is_authenticated else 'anonymous',
            'query_count': query_count,
            'total_time': f"{total_time:.3f}s",
            'db_time': f"{db_time:.3f}s",
            'python_time': f"{(total_time - db_time):.3f}s"
        }
        
        # Log slow queries
        self._log_slow_queries(queries)
        
        # Log request summary
        if total_time > self.SLOW_QUERY_THRESHOLD:
            logger.warning(f"Slow request detected: {log_data}")
        else:
            logger.info(f"Request processed: {log_data}")
    
    def _log_slow_queries(self, queries: list) -> None:
        """Log details of slow queries."""
        for index, query in enumerate(queries, 1):
            query_time = float(query.get('time', 0))
            if query_time > (self.SLOW_QUERY_THRESHOLD / 2):
                logger.warning(
                    f"Slow query #{index}\n"
                    f"Time: {query_time:.3f}s\n"
                    f"SQL: {query.get('sql', 'N/A')}\n"
                )

    def process_exception(self, request: HttpRequest, exception: Exception) -> None:
        """Handle exceptions during request processing."""
        logger.error(
            f"Exception during request: {request.path}\n"
            f"Error: {str(exception)}",
            exc_info=True
        )
