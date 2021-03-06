from django.shortcuts import render
from .auth import auth, Auth

def main(request):
    code = request.GET.get('code')
    access_token = ''
    if code:
        access_token = Auth(code)
    return render(request,'index.html',{'auth':auth,'access_token':access_token})