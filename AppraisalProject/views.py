import calendar
from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import *
import io
from django.core.files.base import ContentFile
from .utils import merge_uploads_to_pdf
from datetime import datetime


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
    departments = Department.objects.all()
    activities = Activities.objects.all()
    acadYear = f"Jan {datetime.now().year} - Dec {datetime.now().year}"
    months = [calendar.month_name[i] for i in range(1, 13)]
    department = request.POST.get('department')
    month = request.POST.get('month')
    activityName = None
    submitted = False

    if request.method == 'POST':
        activityName = request.POST.get('activityName')
        print("Got activityName in Home:", repr(activityName))
        submitted = True   # first form submit aayiduchu

    if not request.user.is_authenticated:
        return redirect('login')

    if request.user.role == 'dean':
        return render(request, 'dean/home.html', {'user': request.user})

    elif request.user.role == 'hod':
        totalFaculty = CreateUser.objects.filter(role='faculty', department=request.user.department).count()
        return render(request, 'hod/home.html', {'user': request.user, 'totalFaculty': totalFaculty ,'acadYear': acadYear})

    elif request.user.role == 'faculty':
        return render(
            request,
            'faculty/home.html',
            {
                'user': request.user,
                'acadYear': acadYear,
                'departments': departments,
                'activities': activities,
                'department': department,
                'month': month,
                'months': months,
                'submitted': submitted,
                'activityName': activityName,
            },
        )
    else:
        return render(request, '404.html')

    
def submit_activity(request):
    if request.method != 'POST':
        return render(request, '404.html')

    activityName = request.POST.get('activityName')
    print("Got activityName:", repr(activityName))
    department = request.POST.get("department")
    month = request.POST.get("month")
    activityRelation = Activities.objects.get(id=activityName)
    departmentName=Department.objects.get(departmentName=department)
    proofs = []   # always define outside
#IAE DETAILS
    if activityName == "1":
        proofs = [
    request.FILES.get("firstYearProof"),
    request.FILES.get("secondYearProof"),
    request.FILES.get("thirdYearProof"),
    request.FILES.get("fourthYearProof"),
]
        details = {
            'firstYearPercent': request.POST.get("firstYear"),
            'secondYearPercent': request.POST.get("secondYear"),
            'thirdYearPercent': request.POST.get("thirdYear"),
            'fourthYearPercent': request.POST.get("fourthYear"),
            'iaeDetail': request.POST.get("iaeDetail"),
        }
#camu
    elif activityName == "2":
        proofs = [
        request.FILES.get("firstYearProof"),
        request.FILES.get("secondYearProof"),
        request.FILES.get("thirdYearProof"),
        request.FILES.get("fourthYearProof"),
    ]
        details = {
            'firstYear': request.POST.get("firstYear"),
            'secondYear': request.POST.get("secondYear"),
            'thirdYear': request.POST.get("thirdYear"),
            'fourthYear': request.POST.get("fourthYear"),
        }

#saturday
#patent/copy rights
    elif activityName == "16":
        proofs = [
        request.FILES.get("patentProof"),
    ]
        details = {
            'patentTitle': request.POST.get("patentTitle"),
            'patentNumber': request.POST.get("patentNumber"),
            'patentStatus': request.POST.get("patentStatus"),
        }
#----------------------------------------------all activities above this line-------------------------------------------------------------
    proofs = [f for f in proofs if f]  # filter None values
    merged_file_field = None
    if proofs:
        buf = io.BytesIO()
        merge_uploads_to_pdf(proofs, buf)   # 👈 function implement pannano
        buf.seek(0)
        merged_file_field = ContentFile(buf.read(), name=f"IAE_{request.user.id}.pdf")
        # save activity
    try:
        ActivitySubmission.objects.create(
                user=request.user,
                department=departmentName,
                month=month,
                activity_name=activityRelation,
                detail=details,
                merged_proof=merged_file_field,
        )
        return render(request, 'faculty/home.html', {'activitySubmitted': True, 'activityName': activityName})
    except Exception as e:
        messages.error(request, 'There was an error submitting your activity. Please try again.')
        print(e)
        return render(request, 'faculty/home.html', {'activitySubmitted': True, 'error': True})