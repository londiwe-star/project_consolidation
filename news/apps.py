"""
Django app configuration for the news application.

This module configures the news app and ensures that signal handlers
are imported when the app is ready.
"""
from django.apps import AppConfig


class NewsConfig(AppConfig):
    """
    Configuration class for the news application.
    
    This class handles app initialization and ensures that Django signals
    are properly registered when the application starts.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'news'

    def ready(self):
        """
        Import signals when the app is ready.
        
        This method is called when Django starts up and ensures that
        all signal handlers in the signals module are registered.
        """
        import news.signals
