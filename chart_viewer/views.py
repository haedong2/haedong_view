from django.shortcuts import render
from django.http import HttpResponse
import pymysql


# Create your views here.
from chart_viewer.models import get_chart_data


def index(request):
    return render(request, 'chart_viewer/index.html', {})


def chart(request):
    return render(request, 'chart_viewer/charts/viewer.html', {})


def get_chart(request):
    result = get_chart_data()

    # for i in range(0, len(result)):
    #     result[i]['date'] = str(result[i]['date'])
    #     result[i]['date'] = result[i]['date'][0:4] + result[i]['date'][4:6] + result[i]['date'][6:12]
    #     result[i].pop('id', None)

    for i in range(0, len(result)):
        temp_result = result[i]
        result[i] = [temp_result['date'], temp_result['open'], temp_result['high'], temp_result['low'], temp_result['close']]

    return render(request, 'chart_viewer/charts/viewer.html', {'data': result[:1000]})
