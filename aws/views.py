from django.shortcuts import render

# Create your views here.


def index(request):
    print("hello")
    return render(request, 'aws/index.html', context={})
