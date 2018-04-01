import time
from turtledemo.penrose import star

from django.shortcuts import render
from django.http import HttpResponse
import pymysql


# Create your views here.
from django.template import RequestContext

import chart_viewer.models as db
from django.http import JsonResponse

def index(request):
    return render(request, 'chart_viewer/index.html', {})


def viewer(request):
    return render(request, 'chart_viewer/charts/viewer.html', {})


def get_data(request):
    proc_start_time = time.time()
    print('request params %s' % request.GET)

    subject_code = request.GET['subject_code']
    start_date = request.GET['start_date'].split('/')
    start_date = '%s-%s-%s' % (start_date[2], start_date[0], start_date[1])
    end_date = request.GET['end_date'].split('/')
    end_date = '%s-%s-%s' % (end_date[2], end_date[0], end_date[1])

    if request.GET['chart_type'] == 'tick':
        result = db.get_tick_data(subject_code, int(request.GET['time_unit']), start_date, end_date)
    else:
        pass

    for i in range(0, len(result)):
        temp_result = result[i]
        result[i] = [temp_result['date'], temp_result['open'], temp_result['high'], temp_result['low'], temp_result['close']]
    proc_end_time = time.time()

    print('processing time : %s' % (proc_end_time - proc_start_time))

    return JsonResponse({'candles': result})


def exist_table(request, subject_code):
    print('exsit_table? %s' % subject_code)
    res = db.exist_table(subject_code)

    return HttpResponse(res)


def get_subject_date(request, subject_code):
    res = db.get_subject_date(subject_code)

    return JsonResponse(res[0])