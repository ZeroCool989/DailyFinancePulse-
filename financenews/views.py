# Import necessary modules and classes
from django.shortcuts import render, get_object_or_404, reverse
from django.views import generic, View
from django.http import HttpResponseRedirect
from .models import Post
from .forms import CommentForm

# Define a view to list blog posts
class PostList(generic.ListView):
    model = Post  # Specify the model to be used for the list view
    queryset = Post.objects.filter(status=1).order_by("-created_on")  # Retrieve published posts
    template_name = "index.html"  # Set the HTML template for the list view
    paginate_by = 6  # Limit the number of posts per page for pagination

# Define a view to display a single blog post along with its comments
class PostDetail(View):
    def get(self, request, slug, *args, **kwargs):
        # Retrieve all published posts
        queryset = Post.objects.filter(status=1)

        # Get the specific post based on the provided slug; return 404 if not found or not published.
        post = get_object_or_404(queryset, slug=slug)

        # Retrieve all approved comments for the post, sorted from newest to oldest.
        comments = post.comments.filter(approved=True).order_by("-created_on")

        # Check if the current logged-in user has liked this post.
        liked = False
        if post.likes.filter(id=self.request.user.id).exists():
            liked = True

        # Render the post detail template, passing the post, its comments, and a new comment form.
        return render(
            request,
            "post_detail.html",
            {
                "post": post,
                "comments": comments,
                "commented": False,
                "liked": liked,
                "comment_form": CommentForm()
            },
        )
        
    def post(self, request, slug, *args, **kwargs):
        # Retrieve all published posts
        queryset = Post.objects.filter(status=1)
        post = get_object_or_404(queryset, slug=slug)
        comments = post.comments.filter(approved=True).order_by("-created_on")
        liked = False
        if post.likes.filter(id=self.request.user.id).exists():
            liked = True

        # Create a comment form instance with the submitted POST data.
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            # Set email and name for the comment from the logged-in user
            comment_form.instance.email = request.user.email
            comment_form.instance.name = request.user.username
            # Create a new comment object from the form but don't save it to the database yet.
            comment = comment_form.save(commit=False)
            comment.post = post
            comment.save()
            # Reset the comment form after a successful submission
            comment_form = CommentForm()
        else:
            # Comment form is not valid, keep the existing form for user correction
            pass

        # Render the post detail template with updated information
        return render(
            request,
            "post_detail.html",
            {
                "post": post,
                "comments": comments,
                "commented": True,
                "comment_form": comment_form,
                "liked": liked
            },
        )

# Define a view to handle liking and unliking a blog post
class PostLike(View):
    def post(self, request, slug, *args, **kwargs):
        # Retrieve the post using the provided slug
        post = get_object_or_404(Post, slug=slug)

        # Check if the current user has already liked the post.
        if post.likes.filter(id=request.user.id).exists():
            post.likes.remove(request.user)  # Remove the user from the post's likes
        else:
            post.likes.add(request.user)  # Add the user to the post's likes

        # Redirect the user back to the post detail page after the action.
        return HttpResponseRedirect(reverse('post_detail', args=[slug]))
