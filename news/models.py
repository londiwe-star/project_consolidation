"""
Models for the news application.

This module defines the core data models for the news platform:
- CustomUser: Extended user model with role-based access control
- Publisher: News organization/publisher entities
- Article: News articles with approval workflow
- Newsletter: Newsletter content model

The models implement role-based permissions and relationships between
users, publishers, journalists, and articles.
"""
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.core.exceptions import ValidationError


class Publisher(models.Model):
    """Model representing a news publisher organization."""
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True)
    logo = models.ImageField(upload_to='publishers/', blank=True, null=True)
    website = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class CustomUser(AbstractUser):
    """
    Custom user model with role-based fields.
    Roles: Reader, Editor, Journalist
    """
    ROLE_CHOICES = [
        ('reader', 'Reader'),
        ('editor', 'Editor'),
        ('journalist', 'Journalist'),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='reader')
    bio = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    
    # Reader-specific fields
    subscribed_publishers = models.ManyToManyField(
        Publisher,
        related_name='subscribers',
        blank=True,
        help_text='Publishers this reader is subscribed to'
    )
    subscribed_journalists = models.ManyToManyField(
        'self',
        symmetrical=False,
        related_name='reader_subscribers',
        blank=True,
        help_text='Journalists this reader is subscribed to'
    )
    
    # Journalist-specific fields
    affiliated_publishers = models.ManyToManyField(
        Publisher,
        related_name='journalists',
        blank=True,
        help_text='Publishers this journalist is affiliated with'
    )

    class Meta:
        ordering = ['username']
        swappable = 'AUTH_USER_MODEL'

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

    def save(self, *args, **kwargs):
        """Override save to automatically assign user to appropriate group based on role."""
        is_new = self.pk is None
        old_role = None
        if not is_new:
            try:
                old_role = CustomUser.objects.get(pk=self.pk).role
            except CustomUser.DoesNotExist:
                pass
        
        super().save(*args, **kwargs)
        
        if is_new or (old_role and old_role != self.role):
            self.assign_to_group()

    def assign_to_group(self):
        """Assign user to the appropriate group based on their role."""
        # Remove user from all role-based groups
        self.groups.clear()
        
        # Get or create the appropriate group and assign user
        group_name = self.get_role_display()
        group, created = Group.objects.get_or_create(name=group_name)
        
        if created:
            self.set_group_permissions(group, self.role)
        
        self.groups.add(group)

    @staticmethod
    def set_group_permissions(group, role):
        """Set appropriate permissions for a group based on role."""
        from django.contrib.contenttypes.models import ContentType
        
        try:
            article_ct = ContentType.objects.get(app_label='news', model='article')
            newsletter_ct = ContentType.objects.get(app_label='news', model='newsletter')
            
            if role == 'reader':
                # Readers can only view articles and newsletters
                permissions = Permission.objects.filter(
                    content_type__in=[article_ct, newsletter_ct],
                    codename__startswith='view_'
                )
            elif role == 'editor':
                # Editors can view, change, and delete articles and newsletters
                permissions = Permission.objects.filter(
                    content_type__in=[article_ct, newsletter_ct],
                    codename__in=[
                        'view_article', 'change_article', 'delete_article',
                        'view_newsletter', 'change_newsletter', 'delete_newsletter'
                    ]
                )
            elif role == 'journalist':
                # Journalists can create, view, change, and delete articles and newsletters
                permissions = Permission.objects.filter(
                    content_type__in=[article_ct, newsletter_ct]
                )
            else:
                permissions = []
            
            group.permissions.set(permissions)
        except ContentType.DoesNotExist:
            # Models don't exist yet during initial migration, skip permission setup
            pass


class Article(models.Model):
    """Model representing a news article."""
    title = models.CharField(max_length=300)
    content = models.TextField()
    summary = models.TextField(max_length=500, blank=True)
    author = models.ForeignKey(
        'CustomUser',
        on_delete=models.CASCADE,
        related_name='articles',
        limit_choices_to={'role': 'journalist'}
    )
    publisher = models.ForeignKey(
        Publisher,
        on_delete=models.CASCADE,
        related_name='articles',
        null=True,
        blank=True,
        help_text='Leave blank for independent journalist articles'
    )
    featured_image = models.ImageField(upload_to='articles/', blank=True, null=True)
    is_approved = models.BooleanField(default=False)
    approved_by = models.ForeignKey(
        'CustomUser',
        on_delete=models.SET_NULL,
        related_name='approved_articles',
        null=True,
        blank=True,
        limit_choices_to={'role': 'editor'}
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        permissions = [
            ('approve_article', 'Can approve article'),
        ]

    def __str__(self):
        status = "Approved" if self.is_approved else "Pending"
        return f"{self.title} - {status}"

    def clean(self):
        """Validate that author is a journalist."""
        # Use author_id to avoid triggering a RelatedObjectDoesNotExist when author isn't set yet
        if self.author_id is not None and self.author.role != 'journalist':
            raise ValidationError({'author': 'Author must have the Journalist role.'})


class Newsletter(models.Model):
    """Model representing a newsletter."""
    title = models.CharField(max_length=300)
    content = models.TextField()
    author = models.ForeignKey(
        'CustomUser',
        on_delete=models.CASCADE,
        related_name='newsletters',
        limit_choices_to={'role': 'journalist'}
    )
    publisher = models.ForeignKey(
        Publisher,
        on_delete=models.CASCADE,
        related_name='newsletters',
        null=True,
        blank=True
    )
    is_sent = models.BooleanField(default=False)
    sent_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} by {self.author.username}"
