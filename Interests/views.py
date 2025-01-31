from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views.generic import CreateView, UpdateView, DeleteView, ListView, DetailView, RedirectView, TemplateView, View
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Count

from Interests.forms import InterestForm
from Interests.models import Interest
from Interests.utils import find_people
from topics.models import Comment
from users.models import User, UserRoles


class InterestCreate(CreateView):
    model = Interest
    form_class = InterestForm

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.user.role in (UserRoles.MODERATOR, UserRoles.ADMIN,):
                return super().dispatch(request, *args, **kwargs)
        raise PermissionDenied()



class InterestUpdate(UpdateView):
    model = Interest
    fields = ['name', 'description']


class InterestDelete(DeleteView):
    model = Interest


class InterestListView(ListView):
    model = Interest

    def get_queryset(self):
        return super().get_queryset().annotate(
            related_count=Count('members')
        ).order_by('-related_count')


class InterestDetailView(DetailView):
    model = Interest

    def get_context_data(self, **kwargs):
        contex = super().get_context_data(**kwargs)
        contex['comments'] = get_object_or_404(Interest, pk=self.kwargs['pk']).comments.order_by('-created_at')[:3]
        contex['topics'] = get_object_or_404(Interest, pk=self.kwargs['pk']).topics.annotate(num_comments=Count('comments')).order_by('-num_comments')[:3]
        return contex


class FindSimilarUser(LoginRequiredMixin, RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        current_user = self.request.user
        founded_user = find_people(current_user)
        self.request.session['found-user'] = founded_user
        return reverse_lazy('interests:user-found')


class FoundSimilarUserView(LoginRequiredMixin, TemplateView):
    template_name = 'Interests/people_find.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        found_user = self.request.session.get('found-user', {})
        context['found_user'] = found_user
        return context

    def get_template_names(self):
        found_user = self.request.session.get('found-user', {})
        if found_user:
            self.request.session['found-user'] = None
            return 'Interests/people_find.html'
        else:
            return 'Interests/not_found.html'


class DenySimilarUserView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        current_user = self.request.user
        added_user = get_object_or_404(User, pk=request.POST.get('user-id'))
        current_user.denied_users.add(added_user)
        founded_user = find_people(current_user)
        if founded_user:
            new_object = render(request, 'includes/user_detail.html', {'object': founded_user}).content.decode()
            response = {'success': True, 'new_object': new_object, 'new_object_id': founded_user.pk}
            return JsonResponse(response)
        else:
            return JsonResponse({'success': True, 'new_object_id': 'none'})


class ApproveSimilarUserView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        current_user = self.request.user
        added_user = get_object_or_404(User, pk=request.POST.get('user-id'))
        current_user.approved_users.add(added_user)
        founded_user = find_people(current_user)
        if founded_user:
            new_object = render(request, 'includes/user_detail.html', {'object': founded_user}).content.decode()
            response = {'success': True, 'new_object': new_object, 'new_object_id': founded_user.pk}
            return JsonResponse(response)
        else:
            return JsonResponse({'success': True, 'new_object_id': 'none'})


class ToggleInterestView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        interest_id = kwargs.get('pk')
        interest = Interest.objects.get(id=interest_id)
        user = request.user
        if user in interest.members.all():
            interest.members.remove(user)
        else:
            interest.members.add(user)
        return JsonResponse({'success': True})


class InterestCommentsListView(ListView):
    model = Comment
    template_name = 'Interests/comment_list.html'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(interest_id=self.kwargs['pk'])
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object'] = get_object_or_404(Interest, pk=self.kwargs['pk'])
        return context

