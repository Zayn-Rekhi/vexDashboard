from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from blog.models import Post
from django.contrib.auth.models import User
from django.views.generic import (ListView, DetailView, CreateView,
                                  UpdateView, DeleteView)
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

# Create your views here.


class PostListView(ListView):

    model = Post
    template_name = 'pages/blog.html'
    context_object_name = 'posts'
    ordering = ['-date_posted']




class PostDetailView(DetailView):

    model = Post
    context_object_name = 'post'
    template_name = 'pages/blog_text.html'



class PostCreateView(LoginRequiredMixin, CreateView):

    model = Post
    fields = ['title', 'content']
    success_url = reverse_lazy('blog:blog-home')

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostUpdatView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):

    model = Post
    fields = ['title', 'content']
    success_url = reverse_lazy('blog:blog-home')

    def test_func(self):
        post = self.get_object()
        return post.author == self.request.user


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):

    model = Post
    success_url = reverse_lazy('blog:blog-home')
    context_object_name = 'post'

    def test_func(self):
        post = self.get_object()
        return post.author == self.request.user


