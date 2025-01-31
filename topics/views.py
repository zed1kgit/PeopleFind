from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse, Http404
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView, View, ListView

from Interests.models import Interest
from topics.forms import TopicForm
from topics.models import Topic, Comment


class TopicCreateView(LoginRequiredMixin, CreateView):
    model = Topic
    form_class = TopicForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object'] = get_object_or_404(Interest, pk=self.kwargs['pk'])
        return context

    def get_success_url(self):
        return reverse_lazy('interests:detail', kwargs={'pk': self.kwargs['pk']})

    def form_valid(self, form):
        self.object = form.save()
        self.object.author = self.request.user
        self.object.interest = get_object_or_404(Interest, pk=self.kwargs['pk'])
        self.object.save()
        return super().form_valid(form)


class CommentCreateView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        user = self.request.user
        text = request.POST['text']
        interest = None
        topic = None
        if request.POST['interest']:
            interest = get_object_or_404(Interest, pk=request.POST['interest'])
        elif request.POST['topic']:
            topic = get_object_or_404(Topic, pk=request.POST['topic'])
        comment = Comment.objects.create(user=user, text=text, interest=interest, topic=topic)
        user.comments.add(comment)
        return JsonResponse({'success': True})


class TopicDetailView(ListView):
    model = Comment
    template_name = 'topics/topic_detail.html'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        topic_id = get_object_or_404(Topic, slug=self.kwargs['slug']).pk
        queryset = queryset.filter(topic_id=topic_id)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object'] = get_object_or_404(Topic, slug=self.kwargs['slug'])
        return context


class TopicListView(ListView):
    model = Topic
    template_name = 'topics/topic_list.html'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        try:
            interest = get_object_or_404(Interest, pk=self.kwargs['pk']).pk
            queryset = queryset.filter(interest_id=interest)
            return queryset
        except Http404:
            return []

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object'] = get_object_or_404(Interest, pk=self.kwargs['pk'])
        return context