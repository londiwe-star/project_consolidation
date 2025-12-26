"""
Views for the news application.

This module contains all view functions for the news platform, including:
- Authentication views (login, register, logout)
- Article management views (CRUD operations)
- Dashboard views for different user roles (reader, journalist, editor)
- Publisher and journalist profile views
- Subscription management views

All views implement proper permission checks and role-based access control.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from .models import Article, Publisher, CustomUser, Newsletter
from .forms import (
    CustomUserCreationForm, ArticleForm, 
    LoginForm, ArticleApprovalForm, PublisherForm
)


def home_view(request):
    """Home page showing approved articles."""
    articles = Article.objects.filter(is_approved=True).select_related(
        'author', 'publisher'
    )[:10]
    
    context = {
        'articles': articles,
    }
    return render(request, 'news/home.html', context)


def register_view(request):
    """User registration view."""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'Account created successfully for {user.username}!')
            login(request, user)
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'news/register.html', {'form': form})


def login_view(request):
    """User login view."""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {user.username}!')
                return redirect('home')
            else:
                messages.error(request, 'Invalid username or password.')
    else:
        form = LoginForm()
    
    return render(request, 'news/login.html', {'form': form})


@login_required
def logout_view(request):
    """User logout view."""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('login')


@login_required
def article_list_view(request):
    """List all approved articles."""
    articles = Article.objects.filter(is_approved=True).select_related(
        'author', 'publisher'
    ).order_by('-published_at')
    
    context = {
        'articles': articles,
    }
    return render(request, 'news/article_list.html', context)


@login_required
def article_detail_view(request, pk):
    """View a single article."""
    article = get_object_or_404(Article, pk=pk)
    
    # Only show approved articles to non-staff users
    if not request.user.is_staff and not article.is_approved:
        messages.error(request, 'This article is not available.')
        return redirect('article_list')
    
    context = {
        'article': article,
    }
    return render(request, 'news/article_detail.html', context)


@login_required
@permission_required('news.add_article', raise_exception=True)
def article_create_view(request):
    """Create a new article (journalists only)."""
    if request.user.role != 'journalist':
        messages.error(request, 'Only journalists can create articles.')
        return redirect('home')
    
    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            article = form.save(commit=False)
            article.author = request.user
            article.save()
            messages.success(request, 'Article created successfully! Awaiting approval.')
            return redirect('journalist_dashboard')
    else:
        form = ArticleForm(user=request.user)
    
    return render(request, 'news/article_form.html', {'form': form, 'action': 'Create'})


@login_required
@permission_required('news.change_article', raise_exception=True)
def article_update_view(request, pk):
    """Update an existing article."""
    article = get_object_or_404(Article, pk=pk)
    
    # Only author or editors can update
    if request.user.role == 'journalist' and article.author != request.user:
        messages.error(request, 'You can only edit your own articles.')
        return redirect('article_detail', pk=pk)
    
    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES, instance=article, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Article updated successfully!')
            return redirect('article_detail', pk=pk)
    else:
        form = ArticleForm(instance=article, user=request.user)
    
    return render(request, 'news/article_form.html', {
        'form': form,
        'action': 'Update',
        'article': article
    })


@login_required
@permission_required('news.delete_article', raise_exception=True)
def article_delete_view(request, pk):
    """Delete an article."""
    article = get_object_or_404(Article, pk=pk)
    
    # Only author or editors can delete
    if request.user.role == 'journalist' and article.author != request.user:
        messages.error(request, 'You can only delete your own articles.')
        return redirect('article_detail', pk=pk)
    
    if request.method == 'POST':
        article.delete()
        messages.success(request, 'Article deleted successfully!')
        return redirect('article_list')
    
    return render(request, 'news/article_confirm_delete.html', {'article': article})


@login_required
def journalist_dashboard_view(request):
    """Dashboard for journalists to manage their articles."""
    if request.user.role != 'journalist':
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    articles = Article.objects.filter(author=request.user).order_by('-created_at')
    
    context = {
        'articles': articles,
    }
    return render(request, 'news/journalist_dashboard.html', context)


@login_required
def editor_dashboard_view(request):
    """Dashboard for editors to review and approve articles."""
    if request.user.role != 'editor':
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    pending_articles = Article.objects.filter(is_approved=False).select_related(
        'author', 'publisher'
    ).order_by('-created_at')
    
    approved_articles = Article.objects.filter(is_approved=True).select_related(
        'author', 'publisher'
    ).order_by('-approved_at')[:10]
    
    context = {
        'pending_articles': pending_articles,
        'approved_articles': approved_articles,
    }
    return render(request, 'news/editor_dashboard.html', context)


@login_required
@permission_required('news.change_article', raise_exception=True)
def article_approve_view(request, pk):
    """Approve an article (editors only)."""
    if request.user.role != 'editor':
        messages.error(request, 'Only editors can approve articles.')
        return redirect('home')
    
    article = get_object_or_404(Article, pk=pk)
    
    if request.method == 'POST':
        form = ArticleApprovalForm(request.POST, instance=article)
        if form.is_valid():
            article = form.save(commit=False)
            if article.is_approved:
                article.approved_by = request.user
                article.approved_at = timezone.now()
                article.published_at = timezone.now()
            article.save()
            
            if article.is_approved:
                messages.success(request, 'Article approved and published!')
            else:
                messages.success(request, 'Article status updated.')
            
            return redirect('editor_dashboard')
    else:
        form = ArticleApprovalForm(instance=article)
    
    context = {
        'form': form,
        'article': article,
    }
    return render(request, 'news/article_approve.html', context)


@login_required
def reader_dashboard_view(request):
    """Dashboard for readers to manage subscriptions and view articles."""
    if request.user.role != 'reader':
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    # Get subscribed content
    subscribed_publisher_ids = request.user.subscribed_publishers.values_list('id', flat=True)
    subscribed_journalist_ids = request.user.subscribed_journalists.values_list('id', flat=True)
    
    # Get articles from subscriptions
    subscribed_articles = Article.objects.filter(
        Q(publisher_id__in=subscribed_publisher_ids) |
        Q(author_id__in=subscribed_journalist_ids),
        is_approved=True
    ).select_related('author', 'publisher').order_by('-published_at')[:20]
    
    context = {
        'subscribed_articles': subscribed_articles,
        'subscribed_publishers': request.user.subscribed_publishers.all(),
        'subscribed_journalists': request.user.subscribed_journalists.all(),
    }
    return render(request, 'news/reader_dashboard.html', context)


@login_required
def publisher_list_view(request):
    """List all publishers."""
    publishers = Publisher.objects.all()
    
    context = {
        'publishers': publishers,
    }
    return render(request, 'news/publisher_list.html', context)


@login_required
def publisher_detail_view(request, pk):
    """View a single publisher with their articles."""
    publisher = get_object_or_404(Publisher, pk=pk)
    articles = Article.objects.filter(
        publisher=publisher,
        is_approved=True
    ).select_related('author').order_by('-published_at')[:20]
    
    is_subscribed = False
    if request.user.is_authenticated and request.user.role == 'reader':
        is_subscribed = request.user.subscribed_publishers.filter(pk=pk).exists()
    
    context = {
        'publisher': publisher,
        'articles': articles,
        'is_subscribed': is_subscribed,
    }
    return render(request, 'news/publisher_detail.html', context)


@login_required
@permission_required('news.add_publisher', raise_exception=True)
def publisher_create_view(request):
    """Create a new publisher (editors only)."""
    if request.user.role != 'editor':
        messages.error(request, 'Only editors can create publishers.')
        return redirect('publisher_list')

    if request.method == 'POST':
        form = PublisherForm(request.POST, request.FILES)
        if form.is_valid():
            publisher = form.save()
            messages.success(request, f'Publisher "{publisher.name}" created successfully!')
            return redirect('publisher_detail', pk=publisher.pk)
    else:
        form = PublisherForm()

    return render(request, 'news/publisher_form.html', {'form': form, 'action': 'Create'})


@login_required
def toggle_publisher_subscription(request, pk):
    """Toggle subscription to a publisher."""
    if request.user.role != 'reader':
        messages.error(request, 'Only readers can subscribe to publishers.')
        return redirect('publisher_detail', pk=pk)
    
    publisher = get_object_or_404(Publisher, pk=pk)
    
    if request.user.subscribed_publishers.filter(pk=pk).exists():
        request.user.subscribed_publishers.remove(publisher)
        messages.success(request, f'Unsubscribed from {publisher.name}.')
    else:
        request.user.subscribed_publishers.add(publisher)
        messages.success(request, f'Subscribed to {publisher.name}!')
    
    return redirect('publisher_detail', pk=pk)


@login_required
def journalist_profile_view(request, pk):
    """View a journalist's profile and articles."""
    journalist = get_object_or_404(CustomUser, pk=pk, role='journalist')
    articles = Article.objects.filter(
        author=journalist,
        is_approved=True
    ).select_related('publisher').order_by('-published_at')[:20]
    
    is_subscribed = False
    if request.user.is_authenticated and request.user.role == 'reader':
        is_subscribed = request.user.subscribed_journalists.filter(pk=pk).exists()
    
    context = {
        'journalist': journalist,
        'articles': articles,
        'is_subscribed': is_subscribed,
    }
    return render(request, 'news/journalist_profile.html', context)


@login_required
def toggle_journalist_subscription(request, pk):
    """Toggle subscription to a journalist."""
    if request.user.role != 'reader':
        messages.error(request, 'Only readers can subscribe to journalists.')
        return redirect('journalist_profile', pk=pk)
    
    journalist = get_object_or_404(CustomUser, pk=pk, role='journalist')
    
    if request.user.subscribed_journalists.filter(pk=pk).exists():
        request.user.subscribed_journalists.remove(journalist)
        messages.success(request, f'Unsubscribed from {journalist.username}.')
    else:
        request.user.subscribed_journalists.add(journalist)
        messages.success(request, f'Subscribed to {journalist.username}!')
    
    return redirect('journalist_profile', pk=pk)
