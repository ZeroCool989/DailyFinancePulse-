from django.shortcuts import render, get_object_or_404, reverse
from django.views import generic, View
from django.http import HttpResponseRedirect
from .models import Post
from .forms import CommentForm

class PostList(generic.ListView):
    """
    A view that extends the generic ListView to display a list of blog posts.
    It is intended for the main page where multiple blog posts are listed.
    """
    model = Post  # This specifies that Post is the model to be used.
    queryset = Post.objects.filter(status=1).order_by("-created_on")  # Retrieves only published posts, ordered by their creation date in descending order.
    template_name = "index.html"  # Refers to the HTML template that renders the post list.
    paginate_by = 6  # Limits the number of posts per page to 6 for pagination purposes.

class PostDetail(View):
    """
    A view that extends Django's View class to handle the display and interaction with a single blog post.
    It deals with both GET and POST requests to show post details and handle comment submissions, respectively.
    """
    def get(self, request, slug, *args, **kwargs):
        """
        Handles GET requests. It is triggered when a user requests to view the details of a specific post.
        """
        post = get_object_or_404(Post, slug=slug, status=1)  # Retrieves the specific post using the slug, only if it's published (status=1). Otherwise, it raises a 404 error.
        comments = post.comments.filter(approved=True).order_by('-created_on')  # Fetches all approved comments for this post, sorted by creation date in descending order.
        liked = post.likes.filter(id=request.user.id).exists()  # Checks if the current user has already liked this post, returning True or False.

        # Renders the post detail page with the post data, comments, and a blank comment form.
        return render(request, "post_detail.html", {
            "post": post,
            "comments": comments,
            "commented": False,  # Indicates that the user has not commented yet (used for UI purposes).
            "liked": liked,
            "comment_form": CommentForm()  # Provides an empty form for submitting a new comment.
        })

    def post(self, request, slug, *args, **kwargs):
        """
        Handles POST requests, which occur when a user submits a comment.
        """
        post = get_object_or_404(Post, slug=slug, status=1)  # Retrieves the post in the same way as the GET method.
        comments = post.comments.filter(approved=True).order_by('-created_on')  # Fetches comments to be included in case the form submission fails and the page needs to be re-rendered.
        liked = post.likes.filter(id=request.user.id).exists()  # Check if the user liked the post, similar to the GET method.

        comment_form = CommentForm(data=request.POST)  # Initializes the comment form with data submitted by the user.

        if comment_form.is_valid():
            # If the form passes validation:
            new_comment = comment_form.save(commit=False)  # Temporarily saves the new comment object without committing to the database.
            new_comment.post = post  # Assigns the current post to the comment.
            new_comment.email = request.user.email  # Sets the commenter's email from the user's data.
            new_comment.name = request.user.username  # Sets the commenter's username.
            new_comment.save()  # Finally commits the comment to the database.

            # Re-fetches comments including the new one for immediate display.
            comments = post.comments.filter(approved=True).order_by('-created_on')

        # Re-renders the same post detail page with all comments and resets the comment form.
        return render(request, "post_detail.html", {
            "post": post,
            "comments": comments,
            "commented": True,  # Indicates that the user has now commented.
            "liked": liked,
            "comment_form": CommentForm()  # Resets the form to be empty after submission.
        })
        
class PostLike(View):
    """
    A view to handle the liking and unliking of a blog post.
    It is designed to respond to POST requests triggered when a user clicks the like or unlike button.
    """
    def post(self, request, slug, *args, **kwargs):
        """
        Handles POST requests for liking or unliking a post.
        """
        post = get_object_or_404(Post, slug=slug)  # Retrieves the post using the provided slug.
        
        # Checks if the current user has already liked the post.
        if post.likes.filter(id=request.user.id).exists():
            post.likes.remove(request.user)  # If yes, remove the user from the post's likes.
        else:
            post.likes.add(request.user)  # If no, add the user to the post's likes.

        # Redirects the user back to the post detail page after the action.
        return HttpResponseRedirect(reverse('post_detail', args=[slug]))
