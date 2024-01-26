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
    def get(self, request, slug, *args, **kwargs):
        """
        Retrieves and displays a single blog post along with its comments when a GET request is made.
        """
        # Fetch the post based on the given slug; return 404 if not found or not published.
        post = get_object_or_404(Post, slug=slug, status=1)

        # Retrieve all approved comments for the post, sorted from newest to oldest.
        comments = post.comments.filter(approved=True).order_by('-created_on')

        # Check if the current logged-in user has liked this post.
        liked = post.likes.filter(id=request.user.id).exists()

        # Render the post detail template, passing the post, its comments, and a new comment form.
        return render(request, "post_detail.html", {
            "post": post,
            "comments": comments,
            "commented": False,
            "liked": liked,
            "comment_form": CommentForm()  # Empty form for new comment submission
        })

    def post(self, request, slug, *args, **kwargs):
        """
        Processes the submission of a new comment when a POST request is made.
        """
        # Fetch the post; return 404 if not found or not published.
        post = get_object_or_404(Post, slug=slug, status=1)

        # Pre-fetch comments for the post in case re-rendering is needed due to form errors.
        comments = post.comments.filter(approved=True).order_by('-created_on')

        # Determine if the current user has liked the post.
        liked = post.likes.filter(id=request.user.id).exists()

        # Create a comment form instance with the submitted POST data.
        comment_form = CommentForm(data=request.POST)

        # Check if the submitted form is valid.
        if comment_form.is_valid():
            # Create a new comment object from the form but don't save it to the database yet.
            new_comment = comment_form.save(commit=False)
            # Link the comment to the current post and user details.
            new_comment.post = post
            new_comment.email = request.user.email
            new_comment.name = request.user.username
            # Save the new comment to the database.
            new_comment.save()
            # Redirect to the post detail page, showing the newly added comment.
            return HttpResponseRedirect(reverse('post_detail', args=[slug]))
        else:
            # If the form is not valid, render the post detail page again with form errors.
            return render(request, "post_detail.html", {
                "post": post,
                "comments": comments,
                "commented": False,
                "liked": liked,
                "comment_form": comment_form  # Form with validation errors
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
