from django.urls import path
from . import views

urlpatterns = [
    path("", views.PostListView.as_view(), name="post-list"),
    path("post/<int:pk>/", views.PostDetailView.as_view(), name="post-detail"),
    path("post/edit/<int:pk>/", views.PostEditView.as_view(), name="post-edit"),
    path("post/delete/<int:pk>/", views.PostDeleteView.as_view(), name="post-delete"),
    path(
        "post/<int:post_pk>/comment/delete/<int:pk>/",
        views.CommentDeleteView.as_view(),
        name="comment-delete",
    ),
    path(
        "post/<int:post_pk>/comment/edit/<int:pk>/",
        views.CommentEditView.as_view(),
        name="comment-edit",
    ),
    path(
        "post/<int:post_pk>/comment/<int:pk>/like/",
        views.AddCommentLike.as_view(),
        name="comment-like",
    ),
    path(
        "post/<int:post_pk>/comment/<int:pk>/dislike/",
        views.AddCommentDisLike.as_view(),
        name="comment-dislike",
    ),
    path(
        "post/<int:post_pk>/comment/<int:pk>/reply/",
        views.CommentReplyView.as_view(),
        name="comment-reply",
    ),
    path(
        "post/<int:pk>/like/",
        views.AddLike.as_view(),
        name="like",
    ),
    path(
        "post/<int:pk>/dislike/",
        views.AddDisLike.as_view(),
        name="dislike",
    ),
    path(
        "profile/<int:pk>/",
        views.ProfileView.as_view(),
        name="profile",
    ),
    path(
        "profile/edit/<int:pk>/",
        views.ProfileEditView.as_view(),
        name="profile-edit",
    ),
    path(
        "profile/<int:pk>/followers/",
        views.ListFollowers.as_view(),
        name="list-followers",
    ),
    path(
        "profile/<int:pk>/followers/add/",
        views.AddFollower.as_view(),
        name="add-follower",
    ),
    path(
        "profile/<int:pk>/followers/remove/",
        views.RemoveFollower.as_view(),
        name="remove-follower",
    ),
    path("search/", views.UserSearch.as_view(), name="profile-search"),
    path(
        "notification/<int:notification_pk>/post/<int:post_pk>/",
        views.PostNotification.as_view(),
        name="post-notification",
    ),
    path(
        "notification/<int:notification_pk>/profile/<int:profile_pk>/",
        views.FollowNotification.as_view(),
        name="follow-notification",
    ),
    path(
        "notification/delete/<int:notification_pk>/",
        views.RemoveNotification.as_view(),
        name="notification-delete",
    ),
    path(
        "inbox/",
        views.ListThreads.as_view(),
        name="inbox",
    ),
    path("inbox/create-thread/", views.CreateThreads.as_view(), name="create-thread",),
    path(
        "inbox/<int:pk>/",
        views.ThreadView.as_view(),
        name="thread",
    ),
    path(
        "inbox/<int:pk>/create-message/",
        views.CreateMessage.as_view(),
        name="create-message",
    ),
]
