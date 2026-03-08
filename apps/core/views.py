from django.http import HttpResponse

def home(request):
    return HttpResponse("Server is running now i can use apis")