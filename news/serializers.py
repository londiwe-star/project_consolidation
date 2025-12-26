"""
Serializers for the REST API.

This module provides Django REST Framework serializers for API data serialization:
- ArticleSerializer: Article data with nested author and publisher information
- PublisherSerializer: Publisher information
- JournalistSerializer: Journalist profile data
- NewsletterSerializer: Newsletter content with author and publisher

Serializers handle data transformation between Python objects and JSON format
for API responses.
"""
from rest_framework import serializers
from .models import Article, Publisher, CustomUser, Newsletter


class PublisherSerializer(serializers.ModelSerializer):
    """Serializer for Publisher model."""
    
    class Meta:
        model = Publisher
        fields = ['id', 'name', 'description', 'website', 'created_at']


class JournalistSerializer(serializers.ModelSerializer):
    """Serializer for Journalist (CustomUser with journalist role)."""
    
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'first_name', 'last_name', 'bio', 'email']


class ArticleSerializer(serializers.ModelSerializer):
    """Serializer for Article model."""
    author = JournalistSerializer(read_only=True)
    publisher = PublisherSerializer(read_only=True)
    author_name = serializers.SerializerMethodField()
    publisher_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Article
        fields = [
            'id', 'title', 'summary', 'content', 'author', 'author_name',
            'publisher', 'publisher_name', 'featured_image', 'is_approved',
            'approved_by', 'approved_at', 'created_at', 'updated_at', 'published_at'
        ]
    
    def get_author_name(self, obj):
        return obj.author.get_full_name() or obj.author.username
    
    def get_publisher_name(self, obj):
        return obj.publisher.name if obj.publisher else 'Independent'


class NewsletterSerializer(serializers.ModelSerializer):
    """Serializer for Newsletter model."""
    author = JournalistSerializer(read_only=True)
    publisher = PublisherSerializer(read_only=True)
    
    class Meta:
        model = Newsletter
        fields = [
            'id', 'title', 'content', 'author', 'publisher',
            'is_sent', 'sent_at', 'created_at', 'updated_at'
        ]
