from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, View

from Interests.models import Interest
from Interests.utils import get_interest_or_404, interest_sidebar_context
from topics.forms import TopicForm
from topics.models import Comment, Topic
from users.models import UserRoles

MAX_COMMENT_LENGTH = 2000


def to_int(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def error_response(message, status=400):
    return JsonResponse({'success': False, 'error': message}, status=status)


class TopicCreateView(LoginRequiredMixin, CreateView):
    model = Topic
    form_class = TopicForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object'] = get_interest_or_404(self.request, self.kwargs['pk'])
        context.update(interest_sidebar_context(context['object']))
        context['title'] = context['object'].name
        context['nav_title'] = 'Создание'
        return context

    def get_success_url(self):
        return reverse_lazy('interests:detail', kwargs={'pk': self.kwargs['pk']})

    def form_valid(self, form):
        # раньше топик сохранялся три раза подряд
        form.instance.author = self.request.user
        form.instance.interest = get_object_or_404(Interest, pk=self.kwargs['pk'])
        return super().form_valid(form)


class CommentCreateView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        text = request.POST.get('text', '').strip()
        if not text:
            return error_response('Комментарий не может быть пустым.')
        if len(text) > MAX_COMMENT_LENGTH:
            return error_response(f'Комментарий слишком длинный (максимум {MAX_COMMENT_LENGTH} символов).')

        interest_id = to_int(request.POST.get('interest'))
        topic_id = to_int(request.POST.get('topic'))
        if (interest_id is None) == (topic_id is None):
            return error_response('Нужно указать либо интерес, либо топик.')

        if interest_id is not None:
            target = {'interest': get_object_or_404(Interest, pk=interest_id)}
        else:
            target = {'topic': get_object_or_404(Topic, pk=topic_id)}
        Comment.objects.create(user=request.user, text=text, **target)
        return JsonResponse({'success': True})


class DeleteObjectView(LoginRequiredMixin, View):
    """Удаление комментария или топика его автором или модератором."""

    def post(self, request, *args, **kwargs):
        user = request.user
        comment_id = to_int(request.POST.get('comment'))
        topic_id = to_int(request.POST.get('topic'))

        if comment_id is not None:
            obj = get_object_or_404(Comment, pk=comment_id)
            owner_id = obj.user_id
        elif topic_id is not None:
            obj = get_object_or_404(Topic, pk=topic_id)
            owner_id = obj.author_id
        else:
            return error_response('Не указан объект для удаления.')

        # Раньше стояло "user is comment.user": request.user это SimpleLazyObject,
        # сравнение через is всегда давало False, и автор не мог удалить свое.
        if owner_id == user.pk or user.role in (UserRoles.MODERATOR, UserRoles.ADMIN):
            obj.delete()
            return JsonResponse({'success': True})
        return error_response('Недостаточно прав.', status=403)


class TopicDetailView(ListView):
    model = Comment
    template_name = 'topics/topic_detail.html'
    paginate_by = 10

    def get_queryset(self):
        self.topic = get_object_or_404(
            Topic.objects.select_related('author').annotate(comments_count=Count('comments')),
            slug=self.kwargs['slug'],
            interest_id=self.kwargs['pk'],
        )
        return self.topic.comments.select_related('user').order_by('created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object'] = get_interest_or_404(self.request, self.kwargs['pk'])
        context.update(interest_sidebar_context(context['object']))
        context['topic'] = self.topic
        context['title'] = self.topic.title
        context['nav_title'] = 'Топик'
        return context


class TopicListView(ListView):
    model = Topic
    template_name = 'topics/topic_list.html'
    paginate_by = 10

    def get_queryset(self):
        self.interest = get_interest_or_404(self.request, self.kwargs['pk'])
        return (
            self.interest.topics.select_related('author')
            .annotate(comments_count=Count('comments'))
            .order_by('-created_at')
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object'] = self.interest
        context.update(interest_sidebar_context(self.interest))
        context['title'] = f'Топики: {self.interest.name}'
        context['nav_title'] = 'Топики'
        return context
