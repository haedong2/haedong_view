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
    proc_start_time = time.time()
    print('request params %s' % request.GET)

    start_date = request.GET['start_date']
    end_date = request.GET['end_date']

    result = get_chart_data(start_date, end_date)

    for i in range(0, len(result)):
        temp_result = result[i]
        result[i] = [temp_result['date'], temp_result['open'], temp_result['high'], temp_result['low'], temp_result['close']]
    proc_end_time = time.time()

    print('processing time : %s' % (proc_end_time - proc_start_time))

    return JsonResponse({'candles': result[:1000]})
