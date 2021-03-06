from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic.edit import UpdateView, DeleteView
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import User

from .models import MessageModel, Notification, Post, Comment, ThreadModel, UserProfile
from .forms import MessageForm, PostForm, CommentForm, ThreadForm


# Create your views here.
class PostListView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        logged_in_user = request.user
        posts = Post.objects.filter(
            author__profile__followers__in=[logged_in_user.id]
        ).order_by("-created_on")
        form = PostForm()

        context = {
            "post_list": posts,
            "form": form,
        }

        return render(request, "social/post_list.html", context)

    def post(self, request, *args, **kwargs):
        logged_in_user = request.user
        posts = Post.objects.filter(
            author__profile__followers__in=[logged_in_user.id]
        ).order_by("-created_on")
        form = PostForm(request.POST, request.FILES)

        if form.is_valid():
            new_post = form.save(commit=False)
            new_post.author = request.user
            new_post.save()

        context = {
            "post_list": posts,
            "form": form,
        }

        return render(request, "social/post_list.html", context)


class PostDetailView(LoginRequiredMixin, View):
    def get(self, request, pk, *args, **kwargs):
        post = Post.objects.get(pk=pk)
        form = CommentForm()

        comments = Comment.objects.filter(post=post).order_by("-created_on")

        context = {
            "post": post,
            "form": form,
            "comments": comments,
        }

        return render(request, "social/post_detail.html", context)

    def post(self, request, pk, *args, **kwargs):
        post = Post.objects.get(pk=pk)
        form = CommentForm(request.POST)

        if form.is_valid():
            new_comment = form.save(commit=False)
            new_comment.author = request.user
            new_comment.post = post
            new_comment.save()

        comments = Comment.objects.filter(post=post).order_by("-created_on")

        context = {
            "post": post,
            "form": form,
            "comments": comments,
        }

        notification = Notification.objects.create(
            notification_type=2,
            from_user=request.user,
            to_user=post.author,
            post=post,
        )

        return render(request, "social/post_detail.html", context)


class CommentReplyView(LoginRequiredMixin, View):
    def post(self, request, post_pk, pk, *args, **kwargs):
        post = Post.objects.get(pk=post_pk)
        parent_comment = Comment.objects.get(pk=pk)
        form = CommentForm(request.POST)

        if form.is_valid():
            new_comment = form.save(commit=False)
            new_comment.author = request.user
            new_comment.post = post
            new_comment.parent = parent_comment
            new_comment.save()

        notification = Notification.objects.create(
            notification_type=2,
            from_user=request.user,
            to_user=parent_comment.author,
            comment=new_comment,
        )

        return redirect("post-detail", pk=post_pk)


class PostEditView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    fields = ["body", "image"]
    template_name = "social/post_edit.html"

    def get_success_url(self):
        pk = self.kwargs["pk"]
        return reverse_lazy("post-detail", kwargs={"pk": pk})

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    template_name = "social/post_delete.html"
    success_url = reverse_lazy("post-list")

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author


class CommentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Comment
    template_name = "social/comment_delete.html"

    def get_success_url(self):
        print(self.kwargs)
        pk = self.kwargs["post_pk"]
        return reverse_lazy("post-detail", kwargs={"pk": pk})

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author


class CommentEditView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Comment
    fields = ["comment"]
    template_name = "social/comment_edit.html"

    def get_success_url(self):
        pk = self.kwargs["post_pk"]
        return reverse_lazy("post-detail", kwargs={"pk": pk})

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author


class ProfileView(View):
    def get(self, request, pk, *args, **kwargs):
        profile = UserProfile.objects.get(pk=pk)
        user = profile.user
        posts = Post.objects.filter(author=user).order_by("-created_on")

        followers = profile.followers.all()

        if len(followers) == 0:
            is_following = False

        for follower in followers:
            if follower == request.user:
                is_following = True
                break
            else:
                is_following = False

        number_of_followers = len(followers)

        context = {
            "user": user,
            "profile": profile,
            "posts": posts,
            "number_of_followers": number_of_followers,
            "is_following": is_following,
        }

        return render(request, "social/profile.html", context)

    def post(self, request, pk, *args, **kwargs):
        pass


class ProfileEditView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = UserProfile
    fields = ["name", "bio", "birth_date", "location", "picture"]
    template_name = "social/profile_edit.html"

    def get_success_url(self):
        pk = self.kwargs["pk"]
        return reverse_lazy("profile", kwargs={"pk": pk})

    def test_func(self):
        profile = self.get_object()
        return self.request.user == profile.user


class AddFollower(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        profile = UserProfile.objects.get(pk=pk)
        profile.followers.add(request.user)

        notification = Notification.objects.create(
            notification_type=3,
            from_user=request.user,
            to_user=profile.user,
        )

        return redirect("profile", pk=profile.pk)

    def get(self, request, pk, *args, **kwargs):
        pass


class RemoveFollower(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        profile = UserProfile.objects.get(pk=pk)
        profile.followers.remove(request.user)

        return redirect("profile", pk=profile.pk)


class AddLike(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        post = Post.objects.get(pk=pk)

        is_dislike = False

        for like in post.dislikes.all():
            if like == request.user:
                is_dislike = True
                break

        if is_dislike:
            post.dislikes.remove(request.user)

        is_like = False

        for like in post.likes.all():
            if like == request.user:
                is_like = True
                break

        if not is_like:
            post.likes.add(request.user)

            notification = Notification.objects.create(
                notification_type=1,
                from_user=request.user,
                to_user=post.author,
                post=post,
            )

        else:
            post.likes.remove(request.user)

        next = request.POST.get("next", "/")
        return HttpResponseRedirect(next)


class AddDisLike(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        post = Post.objects.get(pk=pk)

        is_like = False

        for like in post.likes.all():
            if like == request.user:
                is_like = True
                break

        if is_like:
            post.likes.remove(request.user)

        is_dislike = False

        for like in post.dislikes.all():
            if like == request.user:
                is_dislike = True
                break

        if not is_dislike:
            post.dislikes.add(request.user)
        else:
            post.dislikes.remove(request.user)

        next = request.POST.get("next", "/")
        return HttpResponseRedirect(next)


class UserSearch(View):
    def get(self, request, *args, **kwargs):
        query = self.request.GET.get("query")
        profile_list = UserProfile.objects.filter(Q(user__username__icontains=query))

        context = {
            "profile_list": profile_list,
        }

        return render(request, "social/search.html", context)


class ListFollowers(View):
    def get(self, request, pk, *args, **kwargs):
        profile = UserProfile.objects.get(pk=pk)
        followers = profile.followers.all()

        context = {
            "profile": profile,
            "followers": followers,
        }

        return render(request, "social/followers_list.html", context)


class AddCommentLike(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        comment = Comment.objects.get(pk=pk)

        is_dislike = False

        for like in comment.dislikes.all():
            if like == request.user:
                is_dislike = True
                break

        if is_dislike:
            comment.dislikes.remove(request.user)

        is_like = False

        for like in comment.likes.all():
            if like == request.user:
                is_like = True
                break

        if not is_like:
            comment.likes.add(request.user)
            notification = Notification.objects.create(
                notification_type=1,
                from_user=request.user,
                to_user=comment.author,
                comment=comment,
            )

        else:
            comment.likes.remove(request.user)

        next = request.POST.get("next", "/")
        return HttpResponseRedirect(next)


class AddCommentDisLike(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        comment = Comment.objects.get(pk=pk)

        is_like = False

        for like in comment.likes.all():
            if like == request.user:
                is_like = True
                break

        if is_like:
            comment.likes.remove(request.user)

        is_dislike = False

        for like in comment.dislikes.all():
            if like == request.user:
                is_dislike = True
                break

        if not is_dislike:
            comment.dislikes.add(request.user)
        else:
            comment.dislikes.remove(request.user)

        next = request.POST.get("next", "/")
        return HttpResponseRedirect(next)


class PostNotification(View):
    def get(self, request, notification_pk, post_pk, *args, **kwargs):
        notificication = Notification.objects.get(pk=notification_pk)
        post = Post.objects.get(pk=post_pk)

        notificication.user_has_seen = True
        notificication.save()

        return redirect("post-detail", pk=post_pk)


class FollowNotification(View):
    def get(self, request, notification_pk, profile_pk, *args, **kwargs):
        notificication = Notification.objects.get(pk=notification_pk)
        profile = UserProfile.objects.get(pk=profile_pk)

        notificication.user_has_seen = True
        notificication.save()

        return redirect("profile", pk=profile_pk)


class RemoveNotification(View):
    def delete(self, request, notification_pk, *args, **kwargs):
        notification = Notification.objects.get(pk=notification_pk)

        notification.user_has_seen = True
        notification.save()

        return HttpResponse("Success", content_type="text/plain")


class ListThreads(View):
    def get(self, request, *args, **kwargs):
        threads = ThreadModel.objects.filter(
            Q(user=request.user) | Q(receiver=request.user)
        )

        context = {"threads": threads}

        return render(request, "social/inbox.html", context)


class CreateThreads(View):
    def post(self, request, *args, **kwargs):
        form = ThreadForm(request.POST)
        username = request.POST.get("username")

        try:
            receiver = User.objects.get(username=username)
            if ThreadModel.objects.filter(
                user=request.user, receiver=receiver
            ).exists():
                thread = ThreadModel.objects.filter(
                    user=request.user, receiver=receiver
                )
                return redirect("thread", pk=thread.pk)
            elif ThreadModel.objects.filter(
                user=receiver, receiver=request.user
            ).exists():
                thread = ThreadModel.objects.filter(
                    user=receiver, receiver=request.user
                )
                return redirect("thread", pk=thread.pk)

            if form.is_valid():
                thread = ThreadModel(
                    user=request.user,
                    receiver=receiver,
                )
                thread.save()

                return redirect("thread", pk=thread.pk)
        except:
            return redirect("create-thread")

    def get(self, request, *args, **kwargs):
        form = ThreadForm()

        context = {"form": form}

        return render(request, "social/create_thread.html", context)


class ThreadView(View):
    def get(self, request, pk, *args, **kwargs):
        form = MessageForm()
        thread = ThreadModel.objects.get(pk=pk)
        message_list = MessageModel.objects.filter(thread__pk__contains=pk)

        context = {"thread": thread, "form": form, "message_list": message_list}

        return render(request, "social/thread.html", context)


class CreateMessage(View):
    def post(self, request, pk, *args, **kwargs):
        thread = ThreadModel.objects.get(pk=pk)

        if thread.receiver == request.user:
            receiver = thread.user
        else:
            receiver = thread.receiver

        message = MessageModel(
            thread=thread,
            sender_user=request.user,
            receiver_user=receiver,
            body=request.POST.get("message"),
        )
        message.save()

        return redirect("thread", pk=pk)
