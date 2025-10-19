from django.shortcuts import render, get_object_or_404
from .models import BlogPost

def blog_list(request):
    posts = BlogPost.objects.all().order_by('-published_date')
    return render(request, 'blog/blog_list.html', {'posts': posts})

def blog_post(request, pk):
    post = get_object_or_404(BlogPost, pk=pk)
    return render(request, 'blog/blog_post.html', {'post': post})
