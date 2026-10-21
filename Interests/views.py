from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, TemplateView, UpdateView, View

from Interests.forms import InterestForm
from Interests.models import Interest
from Interests.utils import find_people, get_interest_or_404, interest_sidebar_context
from topics.models import Comment
from users.mixins import RoleRequiredMixin
from users.models import User, UserRoles


class InterestCreateView(RoleRequiredMixin, CreateView):
    model = Interest
    form_class = InterestForm
    allowed_roles = (UserRoles.MODERATOR, UserRoles.ADMIN)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Создание интереса'
        context['nav_title'] = 'Создание'
        return context

    def get_success_url(self):
        return reverse_lazy('interests:detail', kwargs={'pk': self.object.pk})


class InterestUpdateView(RoleRequiredMixin, UpdateView):
    model = Interest
    form_class = InterestForm
    allowed_roles = (UserRoles.MODERATOR, UserRoles.ADMIN)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.object.name
        context['nav_title'] = 'Интерес'
        return context

    def get_success_url(self):
        return reverse_lazy('interests:detail', kwargs={'pk': self.object.pk})


class InterestDeleteView(RoleRequiredMixin, DeleteView):
    model = Interest
    template_name = 'Interests/delete.html'
    success_url = reverse_lazy('users:index')
    allowed_roles = (UserRoles.ADMIN,)


class InterestListView(ListView):
    model = Interest

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Интересы'
        context['nav_title'] = 'Интересы'
        return context

    def get_queryset(self):
        return Interest.objects.with_stats(self.request.user).order_by('-members_count', 'name')


class InterestDetailView(DetailView):
    model = Interest

    def get_queryset(self):
        return Interest.objects.with_stats(self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.object.name
        context['nav_title'] = 'Интерес'
        context.update(interest_sidebar_context(self.object))
        context['comments'] = self.object.comments.select_related('user').order_by('-created_at')[:10]
        context['topics'] = (
            self.object.topics.select_related('author')
            .annotate(comments_count=Count('comments'))
            .order_by('-comments_count', '-created_at')[:10]
        )
        return context


class FoundSimilarUserView(LoginRequiredMixin, TemplateView):
    """Показывает случайного человека с общими интересами (без сессионного состояния)."""

    def get(self, request, *args, **kwargs):
        self.found_user = find_people(request.user)
        return super().get(request, *args, **kwargs)

    def get_template_names(self):
        if self.found_user:
            return ['Interests/people_find.html']
        return ['Interests/not_found.html']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Поиск пользователя'
        context['nav_title'] = 'Поиск'
        context['found_user'] = self.found_user
        return context


class RateSimilarUserView(LoginRequiredMixin, View):
    """Общая логика для одобрения и отклонения найденного пользователя."""
    relation = None  # имя M2M-поля текущего пользователя

    def post(self, request, *args, **kwargs):
        try:
            target_pk = int(request.POST.get('user-id', ''))
        except ValueError:
            raise Http404
        target = get_object_or_404(User, pk=target_pk, is_active=True)

        current_user = request.user
        if target.pk != current_user.pk:
            getattr(current_user, self.relation).add(target)

        found_user = find_people(current_user)
        if not found_user:
            return JsonResponse({'success': True, 'new_object_id': 'none'})
        new_object = render(request, 'includes/user_detail.html', {'object': found_user}).content.decode()
        return JsonResponse({'success': True, 'new_object': new_object, 'new_object_id': found_user.pk})


class DenySimilarUserView(RateSimilarUserView):
    relation = 'denied_users'


class ApproveSimilarUserView(RateSimilarUserView):
    relation = 'approved_users'


class ToggleInterestView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        interest = get_object_or_404(Interest, pk=kwargs['pk'])
        if interest.members.filter(pk=request.user.pk).exists():
            interest.members.remove(request.user)
            subscribed = False
        else:
            interest.members.add(request.user)
            subscribed = True
        return JsonResponse({
            'success': True,
            'subscribed': subscribed,
            'members_count': interest.members.count(),
        })


class InterestCommentsListView(ListView):
    model = Comment
    template_name = 'Interests/comment_list.html'
    paginate_by = 10

    def get_queryset(self):
        self.interest = get_interest_or_404(self.request, self.kwargs['pk'])
        return Comment.objects.filter(interest=self.interest).select_related('user').order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object'] = self.interest
        context.update(interest_sidebar_context(self.interest))
        context['title'] = f'Комментарии: {self.interest.name}'
        context['nav_title'] = 'Комментарии'
        return context


class InterestUsersListView(ListView):
    model = Interest
    template_name = 'Interests/users_list.html'
    paginate_by = 30

    def get_queryset(self):
        self.interest = get_interest_or_404(self.request, self.kwargs['pk'])
        return self.interest.members.order_by('name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object'] = self.interest
        context.update(interest_sidebar_context(self.interest))
        context['title'] = 'Пользователи'
        context['nav_title'] = 'Пользователи'
        return context
