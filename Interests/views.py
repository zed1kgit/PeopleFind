from django.shortcuts import render

from Interests.forms import InterestForm
from Interests.models import Interest
from django.views.generic import CreateView, UpdateView, DeleteView, ListView, DetailView
from django.urls import reverse_lazy


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

