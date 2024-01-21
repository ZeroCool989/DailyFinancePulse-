from django.shortcuts import render
from django.views import generic
from .models import Post

# Class-based view to handle the listing of blog posts
class PostList(generic.ListView):
    model = Post  # Specifies the model to be used for this list view

    # Filters the Post objects to only include those with 'status=1' (published),
    # and orders them by 'created_on' in descending order
    queryset = Post.objects.filter(status=1).order_by("-created_on")

    template_name = "index.html"  # The template used to render the post list

    paginate_by = 6  # Number of posts to display per page
