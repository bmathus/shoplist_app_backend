from django.http import JsonResponse
from django.shortcuts import render

def get_hello(request):
    return JsonResponse({"message":"hello"})