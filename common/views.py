from rest_framework.decorators import api_view
from django.http import HttpResponse

@api_view(['GET'])
def index(request):
    return HttpResponse("<h2>Hello World, I am balibabu</h2>")
