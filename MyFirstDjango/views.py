from django.template import loader
from django.shortcuts import render
from django.http.response import HttpResponseRedirect, HttpResponse
from .models import Users, Notes
from hashlib import sha256

authentication = {}

def main(request):
    host,user = authenticate(request)
    authentication.update({host:user})
    info = ''
    if request.method == 'POST':
        user = request.POST.get('user')
        passwd = sha256(request.POST.get('passwd').encode('utf-8')).hexdigest()
        if Users.objects.filter(user=user,passwd=passwd):
            authentication.update({host:user})
            return HttpResponseRedirect(f'profile/?user={user}')
        else:
            info = 'Invalid'
    elif request.method == 'GET':
        logout = request.GET.get('logout')
        if logout:
            authentication.update({host:''})
            return HttpResponseRedirect('/')
    return render(request,'main.html',{'info':info})

def signup(request):
    info = ''
    if request.method == 'POST':
        user = request.POST.get('user')
        passwd = request.POST.get('passwd')
        email = request.POST.get('email').lower()
        if Users.objects.filter(email=email):
            info = 'Email already exists'
        elif Users.objects.filter(user=user):
            info = 'Username already exists'
        else:
            CreateUser(user,passwd,email)
            info = 'Created ' + user
            return render(request,'main.html',{'info':info})
    return render(request,'signup.html',{'info':info})

def profile(request):
    host,user = authenticate(request)
    if not user or authentication[host] != user:
        return HttpResponseRedirect('/')
    notes = Notes.objects.filter(user=user)
    if request.method == 'POST':
        try:
            noteid = int(request.POST.get('noteid')) - 1
            Notes.objects.filter(user=user)[noteid].delete()
            notes = Notes.objects.filter(user=user)
        except TypeError:
            pass
    if not notes:
        return render(request,'profile.html',{'user':user,'hidden':''})
    noteids = [x for x in range(1,len(notes)+1)]
    notes = list(zip(noteids,notes))
    scrollId = request.POST.get('scrollId')
    if scrollId:
        return HttpResponseRedirect(f'/profile?user={user}#{scrollId}')
    return render(request,'profile.html',{'user':user, 'notes':notes, 'hidden':'hidden'})

def createNote(request):
    host,user = authenticate(request)
    if not user or authentication[host] != user:
        return HttpResponseRedirect('/')
    if request.method == 'POST':
        note = request.POST.get('note')
        Notes.objects.create(user=user,notes=note)
        return render(request,'createNote.html',{'user':user}) 
    return render(request,'createNote.html',{'hidden':'hidden','user':user})

def editNote(request):
    host,user = authenticate(request)
    if not user or authentication[host] != user:
        return HttpResponseRedirect('/')
    noteid = int(request.GET.get('noteid')) - 1
    note = Notes.objects.filter(user=user)
    note = note[noteid]
    if request.method == 'POST':
        new_note = request.POST.get('note')
        Notes.objects.filter(user=user,notes=note.notes).update(notes=new_note)
        return render(request,'editNote.html',{'user':user, 'new_note':new_note})
    return render(request,'editNote.html',{'hidden':'hidden','user':user, 'note':note})
    

def CreateUser(user,passwd,email):
    passwd = sha256(passwd.encode('utf-8')).hexdigest()
    Users.objects.create(user=user,passwd=passwd,email=email)

def authenticate(request):
    host = request.META['REMOTE_ADDR']
    user = request.GET.get('user')
    if not user:
        user = False
    return (host,user)