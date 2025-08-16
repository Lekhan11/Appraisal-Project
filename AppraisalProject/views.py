from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required


def Login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Invalid Username or password')
            return render(request, 'login.html')

    return render(request, 'login.html')

@login_required(login_url='login')
def Home(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.role=='dean':
        return render(request, 'dean/home.html', {'user': request.user})
    elif request.user.role=='hod':
        return render(request, 'hod/home.html', {'user': request.user})
    elif request.user.role=='faculty':
        return render(request, 'faculty/home.html', {'user': request.user})
    else:
        return render(request,'404.html')


