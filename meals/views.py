from django.http import HttpResponse

# Homepage
def home(request):
    return HttpResponse("<h1>StudentPlate prototype<h1>")