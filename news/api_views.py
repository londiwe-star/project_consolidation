"""
API views for the REST API.

This module provides RESTful API endpoints using Django REST Framework:
- ArticleViewSet: Filtered article retrieval based on user subscriptions
- PublisherViewSet: Publisher information endpoints
- JournalistViewSet: Journalist profile endpoints

The API implements subscription-based filtering, ensuring users only see
articles from publishers or journalists they are subscribed to.
"""
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from .models import Article, Publisher, CustomUser, Newsletter
from .serializers import (
    ArticleSerializer, PublisherSerializer,
    JournalistSerializer, NewsletterSerializer
)


class IsReaderOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow readers to view articles.
    """
    def has_permission(self, request, view):
        # Allow authenticated users
        return request.user and request.user.is_authenticated


class ArticleViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for retrieving articles based on user subscriptions.
    
    Filters articles to only show those from publishers or journalists
    the authenticated user (reader) is subscribed to.
    """
    serializer_class = ArticleSerializer
    permission_classes = [permissions.IsAuthenticated, IsReaderOrReadOnly]
    
    def get_queryset(self):
        """
        Filter articles based on the authenticated user's subscriptions.
        
        Returns:
        - Articles from publishers the user is subscribed to
        - Articles from journalists the user is subscribed to
        - Only approved articles
        """
        user = self.request.user
        
        # Get subscribed publishers and journalists
        subscribed_publisher_ids = user.subscribed_publishers.values_list('id', flat=True)
        subscribed_journalist_ids = user.subscribed_journalists.values_list('id', flat=True)
        
        # Filter articles
        queryset = Article.objects.filter(
            Q(publisher_id__in=subscribed_publisher_ids) |
            Q(author_id__in=subscribed_journalist_ids),
            is_approved=True
        ).select_related('author', 'publisher').order_by('-published_at')
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def by_publisher(self, request):
        """
        Get articles filtered by a specific publisher.
        Query param: publisher_id
        """
        publisher_id = request.query_params.get('publisher_id')
        
        if not publisher_id:
            return Response(
                {'error': 'publisher_id query parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if user is subscribed to this publisher
        if not request.user.subscribed_publishers.filter(id=publisher_id).exists():
            return Response(
                {'error': 'You are not subscribed to this publisher'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        articles = Article.objects.filter(
            publisher_id=publisher_id,
            is_approved=True
        ).select_related('author', 'publisher').order_by('-published_at')
        
        serializer = self.get_serializer(articles, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_journalist(self, request):
        """
        Get articles filtered by a specific journalist.
        Query param: journalist_id
        """
        journalist_id = request.query_params.get('journalist_id')
        
        if not journalist_id:
            return Response(
                {'error': 'journalist_id query parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if user is subscribed to this journalist
        if not request.user.subscribed_journalists.filter(id=journalist_id).exists():
            return Response(
                {'error': 'You are not subscribed to this journalist'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        articles = Article.objects.filter(
            author_id=journalist_id,
            is_approved=True
        ).select_related('author', 'publisher').order_by('-published_at')
        
        serializer = self.get_serializer(articles, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def subscriptions(self, request):
        """
        Get information about user's subscriptions.
        """
        user = request.user
        
        data = {
            'subscribed_publishers': PublisherSerializer(
                user.subscribed_publishers.all(), many=True
            ).data,
            'subscribed_journalists': JournalistSerializer(
                user.subscribed_journalists.all(), many=True
            ).data,
        }
        
        return Response(data)


class PublisherViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for retrieving publishers.
    """
    queryset = Publisher.objects.all()
    serializer_class = PublisherSerializer
    permission_classes = [permissions.IsAuthenticated]


class JournalistViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for retrieving journalists.
    """
    queryset = CustomUser.objects.filter(role='journalist')
    serializer_class = JournalistSerializer
    permission_classes = [permissions.IsAuthenticated]
