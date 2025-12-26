"""
Django signals for automated actions when articles are approved.

This module implements Django signal handlers that trigger automated actions:
- Email notifications to subscribers when articles are approved
- Automatic posting to X (Twitter) when articles are published
- Tracking of approval status changes

Signals ensure that these actions happen automatically without requiring
explicit calls in the view code.
"""
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.core.mail import send_mass_mail
from django.utils import timezone
from django.conf import settings
import requests
from .models import Article, CustomUser


@receiver(pre_save, sender=Article)
def track_approval_status(sender, instance, **kwargs):
    """Track when an article's approval status changes."""
    if instance.pk:
        try:
            old_instance = Article.objects.get(pk=instance.pk)
            instance._approval_changed = (
                not old_instance.is_approved and instance.is_approved
            )
        except Article.DoesNotExist:
            instance._approval_changed = False
    else:
        instance._approval_changed = False


@receiver(post_save, sender=Article)
def article_approved_actions(sender, instance, created, **kwargs):
    """
    Trigger automated actions when an article is approved:
    1. Send emails to subscribers
    2. Post to X (Twitter)
    """
    # Check if approval status just changed to True
    if hasattr(instance, '_approval_changed') and instance._approval_changed:
        # Update approval timestamp
        if not instance.approved_at:
            instance.approved_at = timezone.now()
            instance.published_at = timezone.now()
            Article.objects.filter(pk=instance.pk).update(
                approved_at=instance.approved_at,
                published_at=instance.published_at
            )
        
        # Send emails to subscribers
        send_article_to_subscribers(instance)
        
        # Post to X (Twitter)
        post_article_to_twitter(instance)


def send_article_to_subscribers(article):
    """
    Send email notification to all subscribers of the article's publisher or journalist.
    """
    subscribers = set()
    
    # Get subscribers of the publisher
    if article.publisher:
        publisher_subscribers = CustomUser.objects.filter(
            role='reader',
            subscribed_publishers=article.publisher
        )
        subscribers.update(publisher_subscribers)
    
    # Get subscribers of the journalist
    journalist_subscribers = CustomUser.objects.filter(
        role='reader',
        subscribed_journalists=article.author
    )
    subscribers.update(journalist_subscribers)
    
    if not subscribers:
        return
    
    # Prepare email content
    subject = f"New Article Published: {article.title}"
    
    # Create article URL (adjust domain as needed)
    article_url = f"{settings.ALLOWED_HOSTS[0]}/articles/{article.id}/"
    
    message_template = f"""
Hello,

A new article has been published that you might be interested in:

Title: {article.title}
Author: {article.author.get_full_name() or article.author.username}
Publisher: {article.publisher.name if article.publisher else 'Independent'}

Summary:
{article.summary or article.content[:200] + '...'}

Read the full article at: {article_url}

Best regards,
News Application Team
    """
    
    # Create mass email list
    emails = []
    for subscriber in subscribers:
        if subscriber.email:
            emails.append((
                subject,
                message_template,
                settings.DEFAULT_FROM_EMAIL,
                [subscriber.email]
            ))
    
    # Send emails
    if emails:
        try:
            send_mass_mail(emails, fail_silently=False)
            print(f"[v0] Sent article notification to {len(emails)} subscribers")
        except Exception as e:
            print(f"[v0] Error sending emails: {str(e)}")


def post_article_to_twitter(article):
    """
    Post article announcement to X (Twitter) using the API.
    Uses Twitter API v2.
    """
    # Check if Twitter credentials are configured
    if not settings.TWITTER_BEARER_TOKEN:
        print("[v0] Twitter API credentials not configured. Skipping tweet.")
        return
    
    # Prepare tweet content (max 280 characters for Twitter)
    tweet_text = f"📰 New Article: {article.title}\n\n"
    
    if article.summary:
        remaining_chars = 280 - len(tweet_text) - 30  # Reserve space for URL
        summary = article.summary[:remaining_chars] + "..." if len(article.summary) > remaining_chars else article.summary
        tweet_text += summary + "\n\n"
    
    # Add article URL
    article_url = f"{settings.ALLOWED_HOSTS[0]}/articles/{article.id}/"
    tweet_text += f"Read more: {article_url}"
    
    # Truncate if still too long
    if len(tweet_text) > 280:
        tweet_text = tweet_text[:277] + "..."
    
    # Twitter API v2 endpoint
    url = "https://api.twitter.com/2/tweets"
    
    headers = {
        "Authorization": f"Bearer {settings.TWITTER_BEARER_TOKEN}",
        "Content-Type": "application/json",
    }
    
    payload = {
        "text": tweet_text
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code == 201:
            print(f"[v0] Successfully posted article to Twitter: {article.title}")
        else:
            print(f"[v0] Failed to post to Twitter. Status: {response.status_code}, Response: {response.text}")
    
    except Exception as e:
        print(f"[v0] Error posting to Twitter: {str(e)}")
