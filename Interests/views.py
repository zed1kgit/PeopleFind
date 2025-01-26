from django.shortcuts import render, get_object_or_404
from django.views.generic import CreateView, UpdateView, DeleteView, ListView, DetailView, RedirectView, TemplateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin

from Interests.forms import InterestForm
from Interests.models import Interest
from Interests.services import find_similar_users, weighted_random_choice
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


class InterestDetailView(DetailView):
    model = Interest


class FindSimilarUser(LoginRequiredMixin, RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        current_user = self.request.user
        similar_users_list = find_similar_users(current_user)
        if len(similar_users_list) > 0:
            found_user_pk = weighted_random_choice(similar_users_list)
            found_user = User.objects.get(pk=found_user_pk)
            self.request.session['found-user'] = found_user
        else:
            self.request.session['found-user'] = None
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
            return 'Interests/people_find.html'
        else:
            return 'Interests/not_found.html'


class DenySimilarUserView(LoginRequiredMixin, RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        current_user = self.request.user
        found_user = self.request.session.get('found-user', {})
        current_user.denied_users.add(found_user)
        return reverse_lazy('interests:find-user')


class ApproveSimilarUserView(LoginRequiredMixin, RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        current_user = self.request.user
        found_user = self.request.session.get('found-user', {})
        current_user.approved_users.add(found_user)
        return reverse_lazy('interests:find-user')

