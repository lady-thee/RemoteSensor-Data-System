from rest_framework import status, generics
from rest_framework.response import Response
from django.http import HttpResponse



def index(request):
    return HttpResponse('Hello')

