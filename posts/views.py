from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator

from .models import User, Post, Group, Follow
from .forms import PostForm, CommentForm


def index(request):
    post_list = Post.objects.select_related('group').all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    return render(
        request,
        'index.html',
        {'page': page, 'paginator': paginator}
    )


@login_required
def follow_index(request):
    post_list = Post.objects.filter(author__following__user=request.user)

    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    return render(
        request,
        'follow.html',
        {'page': page, 'paginator': paginator}
    )


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    user = request.user
    if user != author:
        Follow.objects.get_or_create(user=user, author=author)
    return redirect('follow_index')


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    user = request.user
    relation = Follow.objects.filter(user=user, author=author)
    if relation.exists():
        relation.delete()
    return redirect('follow_index')


def group_post(request, slug):
    group = get_object_or_404(Group, slug=slug)
    group_post_list = group.posts.all()
    paginator = Paginator(group_post_list, 5)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    return render(
        request,
        'group.html',
        {'page': page, 'paginator': paginator, 'group': group}
    )


def profile(request, username):
    author = get_object_or_404(User, username=username)
    user = request.user
    user_posts = author.posts.all()
    paginator = Paginator(user_posts, 5)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    following = not request.user.is_anonymous and Follow.objects.filter(
        user=user,
        author=author
    ).exists()

    return render(
        request,
        'profile.html',
        {
            'page': page,
            'paginator': paginator,
            'author': author,
            'following': following,
        }
    )


def post_view(request, username, post_id):
    post = get_object_or_404(Post, pk=post_id)
    user = request.user
    form = CommentForm(request.POST or None)
    following = not request.user.is_anonymous and Follow.objects.filter(
        user=user,
        author=post.author
    ).exists()

    return render(
        request,
        'post.html',
        {
            'author': post.author,
            'post': post,
            'form': form,
            'items': post.comments.all(),
            'following': following,
        }
    )


@login_required
def add_comment(request, username, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        form.instance.author = request.user
        form.instance.post_id = post_id
        form.save()
    return redirect('post', username=username, post_id=post_id)


@login_required
def new_post(request):
    if request.method != 'POST':
        form = PostForm()
        return render(request, 'new.html', {'form': form})

    form = PostForm(request.POST or None, files=request.FILES or None)
    if form.is_valid():
        new = form.save(commit=False)
        new.author = request.user
        new.save()
        return redirect('index')
    return render(request, 'new.html', {'form': form, 'is_edit': False})


@login_required
def post_edit(request, username, post_id):
    post = get_object_or_404(Post, pk=post_id, author__username=username)
    if post.author != request.user:
        return redirect('post', username=username, post_id=post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if form.is_valid():
        form.save()
        return redirect('post', username=username, post_id=post_id)

    return render(
        request,
        'new.html',
        {'form': form, 'post': post, 'is_edit': True}
    )


def page_not_found(request, exception):
    return render(
        request,
        "misc/404.html",
        {"path": request.path},
        status=404
    )


def server_error(request):
    return render(request, "misc/500.html", status=500)
