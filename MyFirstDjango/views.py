from django.shortcuts import render
from django.http.response import HttpResponseRedirect, HttpResponse
from .models import Users, Notes
from hashlib import sha256

authentication = {}

def main(request):
    info = ''
    if request.method == 'POST':
        user = request.POST.get('user')
        passwd = sha256(request.POST.get('passwd').encode('utf-8')).hexdigest()
        if Users.objects.filter(user=user,passwd=passwd):
            Authenticate(request, login=True, user=user)
            return HttpResponseRedirect(f'profile/')
        else:
            info = 'Invalid'
    elif request.method == 'GET':
        logout = request.GET.get('logout')
        if logout:
            Authenticate(request,logout=True)
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
    user = Authenticate(request)
    if not user:return HttpResponseRedirect('/')
    notes = Notes.objects.filter(user=user)
    search = ''
    info = ''
    search = request.GET.get('q')    
    if search:
        notes = Search(search,user)
    if not notes:
        info = 'You have no notes'
        if search:
            info = 'Nothing found'
    noteids = [x for x in range(1,len(notes)+1)]
    notes = reversed(list(zip(noteids,notes)))
    return render(request,'profile.html',{'user':user, 'notes':notes,'info':info})

def remove(request):
    user = Authenticate(request)
    if not user:return HttpResponseRedirect('/')
    info = ''
    notes = Notes.objects.filter(user=user)
    removeall = request.GET.get('removeall')
    if removeall:
        [ x.delete() for x in notes ]
        notes = Notes.objects.filter(user=user)
    if request.method == 'POST':
        if not removeall:
            notes_to_remove = []
            for ni in range(1,len(notes)+1):
                noterm = request.POST.get(f'noterm{ni}')
                if noterm:
                    notes_to_remove.append(int(noterm)-1)
            if notes_to_remove:
                [ notes[x].delete() for x in notes_to_remove ]
                notes = Notes.objects.filter(user=user)
                info = f"Removed {len(notes_to_remove)} notes"
            else:
                info = 'Select some notes to remove'
                del notes_to_remove, noterm, removeall
    if not notes:
        info = 'You have no notes'
        if removeall:
            info = 'Removed all the notes'
        return render(request,'remove.html',{'user':user, 'info':info})
    noteids = [x for x in range(1,len(notes)+1)]
    notes = reversed(list(zip(noteids,notes)))
    return render(request,'remove.html',{'user':user, 'notes':notes, 'info':info})

def createNote(request):
    user = Authenticate(request)
    if not user:return HttpResponseRedirect('/')
    info = ''
    if request.method == 'POST':
        note = request.POST.get('note')
        if not note:
            info = 'Empty note'
            return render(request,'createNote.html',{'info':info, 'user':user})
        info = 'Created'
        Notes.objects.create(user=user,notes=note)
        return render(request,'createNote.html',{'info':info, 'user':user})
    return render(request,'createNote.html',{'info':info, 'user':user})

def editNote(request):
    user = Authenticate(request)
    if not user:return HttpResponseRedirect('/')
    info = ''
    noteid = request.GET.get('noteid')
    if not noteid:return HttpResponseRedirect('/profile')
    noteid = int(noteid) - 1
    note = Notes.objects.filter(user=user)
    note = note[noteid]
    if request.method == 'POST':
        new_note = request.POST.get('note')
        if not new_note:
            info = 'Empty note'
            return render(request,'editNote.html',{'info':info, 'user':user, 'new_note':new_note})
        info = 'Edited'
        Notes.objects.filter(user=user,notes=note.notes).update(notes=new_note)
        return render(request,'editNote.html',{'info':info, 'user':user, 'new_note':new_note})
    return render(request,'editNote.html',{'info':info, 'user':user, 'note':note})

def CreateUser(user,passwd,email):
    passwd = sha256(passwd.encode('utf-8')).hexdigest()
    Users.objects.create(user=user,passwd=passwd,email=email)

def Authenticate(request,login=False,user=False,logout=False):
    host = request.META['REMOTE_ADDR']
    if login:
        authentication.update({host:user})
        return
    if logout:
        authentication.update({host:user})
        return
    try:
        return authentication[host]    
    except KeyError:
        authentication.update({host:user})
        return authentication[host]

def Search(search,user):
    allnotes = Notes.objects.filter(user=user)
    matched = []
    for note in allnotes:
        if search in note.notes.lower():
            matched.append(note)
    return matched
