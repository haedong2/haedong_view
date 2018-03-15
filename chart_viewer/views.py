from django.shortcuts import render
from django.http import HttpResponse
import pymysql


# Create your views here.
def index(request):

    return render(request, 'chart_viewer/index.html', {})


def chart(request):
    return render(request, 'chart_viewer/charts/viewer.html', {})