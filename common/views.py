from rest_framework.decorators import api_view
from django.shortcuts import render

@api_view(['GET'])
def index(request):
    try:
        with open("/sys/class/power_supply/battery/capacity") as f:
            battery_percent = f.read().strip()
    except FileNotFoundError:
        battery_percent = "Unavailable"
    return render(request, 'common/home.html', {'battery_percent':battery_percent})
