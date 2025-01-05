from django.shortcuts import render

def index(request):
    context = {
        "title": "Gaming Platform",
    }
    return render(request, 'base.html', context)
