from django.shortcuts import render, get_object_or_404
from django.views import generic, View
from .models import Post
from .forms import CommentForm

# Class-based view to handle the listing of blog posts
class PostList(generic.ListView):
    model = Post  # Specifies the model to be used for this list view

    # Filters the Post objects to only include those with 'status=1' (published),
    # and orders them by 'created_on' in descending order
    queryset = Post.objects.filter(status=1).order_by("-created_on")

    template_name = "index.html"  # The template used to render the post list

    paginate_by = 6  # Number of posts to display per page
    
class PostDetail(View):
    def get(self, request, slug, *args, **kwargs):
        # Filters the Post objects to only include those with 'status=1' (published),
        queryset = Post.objects.filter(status=1).order_by("-created_on")
        # Retrieves the post with the given slug, or returns a 404 error
        post = get_object_or_404(Post, slug=slug)
        comment = post.comments.filter(approved=True).order_by('-created_on')
        liked=False
        if post.likes.filter(id=request.user.id).exists():
            liked=True
        return render(
            request, 
            "post_detail.html", 
            {
                "post": post,
                "comment": comment,
                "liked":liked,
                "comment_form": CommentForm()
                }
            )
        # Renders the post detail template with the post object
