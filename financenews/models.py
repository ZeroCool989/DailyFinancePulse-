from django.db import models
from django.contrib.auth.models import User
from cloudinary.models import CloudinaryField

# Status choices for the Post model
STATUS = ((0, "Draft"), (1, "Published"))

class Post(models.Model):
    # Title of the blog post, which is unique for each post
    title = models.CharField(max_length=200, unique=True)

    # A URL-friendly slug, unique for each post
    slug = models.SlugField(max_length=200, unique=True)

    # The author of the post, linked to Django's built-in User model
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="blog_posts"
    )

    # The image associated with the post, stored in Cloudinary
    featured_image = CloudinaryField('image', default='placeholder')

    # A short excerpt or summary of the blog post
    excerpt = models.TextField(blank=True)

    # Auto-updated field every time the post is saved
    update_on = models.DateTimeField(auto_now=True)

    # Main body of the blog post
    content = models.TextField()

    # Timestamp for when the post was created
    created_on = models.DateTimeField(auto_now_add=True)

    # The current status of the post (e.g., Draft or Published)
    status = models.IntegerField(choices=STATUS, default=0)

    # ManyToMany field to track which users liked the post
    likes = models.ManyToManyField(
        User, related_name='blogpost_like', blank=True)

    class Meta:
        # Orders posts so that the most recent is displayed first
        ordering = ["-created_on"]

    def __str__(self):
        # Returns the title when the model instance is converted to a string
        return self.title
    
    # Method to count the number of approved comments for the post
    def number_of_comments(self):
        #Returns the number of approved comments for this post.
        return self.comments.filter(approved=True).count()

    def number_of_likes(self):
        # Counts and returns the number of likes for the post
        return self.likes.count()

class Comment(models.Model):
    # Linking each comment to a specific post
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")

    # Commenter's name
    name = models.CharField(max_length=80)

    # Commenter's email
    email = models.EmailField()

    # Text content of the comment
    body = models.TextField()

    # Automatic timestamp for when comment is made
    created_on = models.DateTimeField(auto_now_add=True)

    # Flag for whether a comment is approved to show
    approved = models.BooleanField(default=False)

    class Meta:
        # Sort comments by the time they were created
        ordering = ["created_on"]

    def __str__(self):
        # String representation showing part of comment and commenter's name
        return f"Comment '{self.body[:20]}...' by {self.name}"
    
    
    

    