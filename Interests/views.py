from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views.generic import CreateView, UpdateView, DeleteView, ListView, DetailView, RedirectView, TemplateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count

from Interests.forms import InterestForm
from Interests.models import Interest
from Interests.utils import find_people
from users.models import User


class InterestCreate(CreateView):
    model = Interest
    form_class = InterestForm
    success_url = reverse_lazy('interests:detail')

    def form_valid(self, form):
        interest = form.save()
        interest.created_by = self.request.user
        interest.save()
        return super().form_valid(form)


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


class DenySimilarUserView(LoginRequiredMixin, RedirectView):
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


class ApproveSimilarUserView(LoginRequiredMixin, RedirectView):
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


class ToggleInterestView(LoginRequiredMixin, RedirectView):
    def post(self, request, *args, **kwargs):
        interest_id = kwargs.get('pk')
        interest = Interest.objects.get(id=interest_id)
        user = request.user
        if user in interest.members.all():
            interest.members.remove(user)
        else:
            interest.members.add(user)
        return JsonResponse({'success': True})
