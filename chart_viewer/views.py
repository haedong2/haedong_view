import time
from turtledemo.penrose import star

from django.shortcuts import render
from django.http import HttpResponse
import pymysql


# Create your views here.
from django.template import RequestContext

from chart_viewer.models import get_chart_data
from django.http import JsonResponse

def index(request):
    return render(request, 'chart_viewer/index.html', {})


def viewer(request):
    return render(request, 'chart_viewer/charts/viewer.html', {})


def get_data(request):
    print('request params %s' % request)
    start_time = time.time()
    result = get_chart_data()

    for i in range(0, len(result)):
        temp_result = result[i]
        result[i] = [temp_result['date'], temp_result['open'], temp_result['high'], temp_result['low'], temp_result['close']]
    end_time = time.time()

    print('return data')
    return JsonResponse({'candles': result[-1000:]})

    # return render(request, 'chart_viewer/chart/viewer.html', {'data': result[:8000]})
