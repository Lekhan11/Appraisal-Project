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


#consultancy
    elif activityName == "17":
        proofs = [
        request.FILES.get("Approvalletter"),
        request.FILE.get("Completionreport"),
        request.FILE.get("Amountreceivedproof")
    ]
        details = {
            'consultancyTitle': request.POST.get("consultancyTitle"),
            'consultancyAmount': request.POST.get("consultancyAmount"),
            'consultancyAgency': request.POST.get("consultancyAgency"),
        }   

#MoU
    elif activityName == "18":
        proofs = [
            request.FILE.get("mouagreement"),
            request.FILE.get("mousigningphotot")
     ]
        details = {
            'company': request.POST.get("company"),
            'date': request.POST.get("date"),
            'duration': request.POST.get("duration"),
            'coordinator1': request.POST.get("coordinator1"),
            'coordinator2': request.POST.get("coordinator2"),
            'activity': request.POST.get("activity"),
            'eventDate': request.POST.get("eventDate"),
            'participants': request.POST.get("participants"),


        }

#industrialguestlecture
    elif activityName == "15":  
        proofs = [
            request.FILES.get("attachproof"),  # Word copy
    ]
        details = {
           'facultyname': request.POST.get("facultyname"),
           'title': request.POST.get("title"),
           'Publisher': request.POST.get("Publisher"),
           'issueNo': request.POST.get("issueNo"),
           'issnNo': request.POST.get("issnNo"),
           'monthYear': request.POST.get("monthYear"),
           'websiteUrl': request.POST.get("websiteUrl"),
    }
#saturday
#patent/copy rights
    elif activityName == "16":
        proofs = [
        request.FILES.get("attachproof"),
    ]
        details = {
            'facultyname': request.POST.get("facultyname"),
            'title': request.POST.get("title"),
            'date': request.POST.get("date"),
        }


#consultancy
    elif activityName == "17":
        proofs = [
        request.FILES.get("attachproof1"),
        request.FILES.get("attachproof2"),
        request.FILES.get("attachproof3")
    ]
        details = {
            'facultyname': request.POST.get("facultyname"),
            'title': request.POST.get("title"),
            'agency': request.POST.get("agency"),
            'fromDate': request.POST.get("fromDate"),
            'duration': request.POST.get("duration"),
            'amount': request.POST.get("amount"),

        }   

#MoU
    elif activityName == "18":
        proofs = [
            request.FILES.get("attachproof1"),
            request.FILES.get("attachproof2")
     ]
        details = {
            'companyname': request.POST.get("companyname"),
            'date': request.POST.get("date"),
            'duration': request.POST.get("duration"),
            'coordinator1': request.POST.get("coordinator1"),
            'coordinator2': request.POST.get("coordinator2"),
            'activityname': request.POST.get("activityname"),
            'eventDate': request.POST.get("eventDate"),
            'participants': request.POST.get("participants"),


        }

#industrialguestlecture
    elif activityName == "19":  
        proofs = [
            request.FILES.get("attachproof1"),        # Resource Person Profile
            request.FILES.get("attachproof2"),  # PDF with all docs
            request.FILES.get("attachproof3")  # Word copy
    ]
        details = {
           'eventtitle': request.POST.get("eventtitle"),
           'resourcePerson': request.POST.get("resourcePerson"),
           'designation': request.POST.get("designation"),
           'phone': request.POST.get("phone"),
           'email': request.POST.get("email"),
           'coordinator1': request.POST.get("coordinator1"),
           'coordinator2': request.POST.get("coordinator2"),
           'eventDate': request.POST.get("eventDate"),
           'participants': request.POST.get("participants"),
    }
        
#facultyintership
# Activite name 20
    elif activityName == "20":   # give a unique ID for this activity
        proofs = [
            request.FILES.get("attachproof1"),       # Geo-tagged Photo
            request.FILES.get("attachproof2")  # Certificate
    ]
        details = {
            'facultyname': request.POST.get("facultyname"),
            'industryname': request.POST.get("industryname"),
            'fromDate': request.POST.get("datefrom"),
            'toDate': request.POST.get("dateto"),
    }
      
# Activite name 21
    elif activityName == "21":
        proofs = [
            request.FILES.get("attachproof1"),
            request.FILES.get("attachproof2"),
        ]
        details = {
            'facultyname': request.POST.get("facultyname"),
            'eventtype': request.POST.get("eventtype"),
            'eventtitle': request.POST.get("eventtitle"),
            'organizer': request.POST.get("organizer"),
            'datefrom': request.POST.get("datefrom"),
            'dateto': request.POST.get("dateto"),

        }


# Activite name 22
    elif activityName == "22":
        proofs = [
            request.FILES.get("supervisororder")
        ]
        details = {
            'facultyname': request.POST.get("facultyname"),
            'noofregstud': request.POST.get("noofregstud"),
            'mode': request.POST.get("mode"),
            'date': request.POST.get("date"),

        }

# Activite name 23
    elif activityName == "23":
        proofs = [
            request.FILES.get("SupervisorOrder"),
            request.FILES.get("Permissionletter")
        ]
        details = {
            'facultyname': request.POST.get("facultyname"),
            'eventtype': request.POST.get("eventtype"),
            'eventtitle': request.POST.get("eventtitle"),
            'datefrom': request.POST.get("datefrom"),
            'dateto': request.POST.get("dateto"),
            'organizer': request.POST.get("organizer"),
            
        }

# Activite name 24
    elif activityName == "24":
        proofs = [
            request.FILES.get("proof")
        ]
        details = {
            'titleofgrant': request.POST.get("titleofgrant"),
            'fundappliedin': request.POST.get("fundappliedin"),
            'nameoffundingagency': request.POST.get("nameoffundingagency"),
            'nameoffacultyappliedfunding': request.POST.get("nameoffacultyappliedfunding"),
            'fundreceived': request.POST.get("fundreceived"),
            'date': request.POST.get("date"),
            'durationofresearch': request.POST.get("durationofresearch"),
        }

# Activite name 25
    elif activityName == "25":
        proofs = [
            request.FILES.get("proof")
        ]
        details = {
            'facultyname': request.POST.get("facultyname"),
            'eventtype': request.POST.get("eventtype"),
            'eventtitle': request.POST.get("eventtitle"),
            'organizer_details': request.POST.get("organizerdetails"),
            'datefrom': request.POST.get("datefrom"),
            'dateto': request.POST.get("dateto"),
        }

# Activite name 26
    elif activityName == "26":
        proofs = [
            request.FILES.get("internshipphotoevidence"),
            request.FILES.get("attachxlfile"),
            request.FILES.get("certificatepdf")
        ]
        details = {
            'studentname': request.POST.get("studentname"),
            'industryname': request.POST.get("industryname"),
            'datefrom': request.POST.get("datefrom"),
            'dateto': request.POST.get("dateto"),
            'mentorname': request.POST.get("mentorname"),
            
        }

# Activite name 27
    elif activityName == "27":
        proofs = [
            request.FILES.get("attachcertificate"),
            request.FILES.get("attachreport")
        ]
        details = {
            'studentname': request.POST.get("studentname"),
            'nameinternalguide': request.POST.get("nameinternalguide"),
            'nameoftheindustywithaddress': request.POST.get("nameoftheindustywithaddress"),
            'datefrom': request.POST.get("datefrom"),
            'dateto': request.POST.get("dateto"),
            'mentorname': request.POST.get("mentorname"),
            
        }                                        

         
        
# Activite name 29
    elif activityName == "29":
        proofs = [
            request.FILES.get("attachproof1"),
            request.FILES.get("attachproof2"),
        ]
        details = {
            'studentname': request.POST.get("studentname"),
            'eventtype': request.POST.get("eventtype"),
            'eventtitle': request.POST.get("eventtitle"),
            'organizer': request.POST.get("organizer"),
            'datefrom': request.POST.get("datefrom"),
            'dateto': request.POST.get("dateto"),
            'mentorname': request.POST.get("mentorname"),
        }

# Activite name 30
    elif activityName == "30":
        proofs = [
            request.FILES.get("attachproof1"),
            request.FILES.get("attachproof2"),
        ]
        details = {
            'studentname': request.POST.get("studentname"),
            'eventtype': request.POST.get("eventtype"),
            'companyname': request.POST.get("companyname"),
            'designation': request.POST.get("designation"),
            'salary': request.POST.get("salary"),
        }

# Activite name 31
    elif activityName == "31":
        proofs = [
            request.FILES.get("attachproof1"),
            request.FILES.get("attachproof2"),
        ]
        details = {
            'studentname': request.POST.get("studentname"),
            'designcontestname': request.POST.get("designcontestname"),
            'organizer': request.POST.get("organizer"),
            'datefrom': request.POST.get("datefrom"),
            'dateto': request.POST.get("dateto"),
            'mentorname': request.POST.get("mentorname"),
        }

# Activite name 32
    elif activityName == "32":
        proofs = [
            request.FILES.get("attachproof1"),
            request.FILES.get("attachproof2"),
        ]
        details = {
            'studentname': request.POST.get("studentname"),
            'facultyname': request.POST.get("facultyname"),
            'coursetitle': request.POST.get("coursetitle"),
            'datefrom': request.POST.get("datefrom"),
            'dateto': request.POST.get("dateto"),
            'mentorname': request.POST.get("mentorname"),
        }

# Activite name 33
    elif activityName == "33":
        proofs = [
            request.FILES.get("attachproof1"),
            request.FILES.get("attachproof2"),
        ]
        details = {
            'facultyname': request.POST.get("facultyname"),
            'eventdescription': request.POST.get("eventdescription"),
            'organizer': request.POST.get("organizer"),
            'datefrom': request.POST.get("datefrom"),
            'dateto': request.POST.get("dateto"),
        }

# Activite name 34
    elif activityName == "34":
        proofs = [
            request.FILES.get("attachproof1"),
            request.FILES.get("attachproof2"),
        ]
        details = {
            'studentname': request.POST.get("studentname"),
            'facultyname': request.POST.get("facultyname"),
            'coursetitle': request.POST.get("coursetitle"),
            'datefrom': request.POST.get("datefrom"),
            'dateto': request.POST.get("dateto"),
            'mentorname': request.POST.get("mentorname"),
        }

# Activite name 35
    elif activityName == "35":
        proofs = [
            request.FILES.get("attachproof1"),
            request.FILES.get("attachproof2"),
        ]
        details = {
            'staffname': request.POST.get("staffname"),
            'subjectname': request.POST.get("subjectname"),
            'year/sem': request.POST.get("year/sem"),
            'methodadopted': request.POST.get("methodadopted"),
            'youtubelink': request.POST.get("youtubelink"),
            
        }


# Activite name 36
    elif activityName == "36":
        proofs = [
            request.FILES.get("attachproof1"),
            request.FILES.get("attachproof2"),
            request.FILES.get("attachproof3")
        ]
        details = {
            'guestname': request.POST.get("guestname"),
            'eventtitle': request.POST.get("eventtitle"),
            'date': request.POST.get("date"),
            'participants': request.POST.get("participants"),
            'programcoordinator1': request.POST.get("programcoordinator1"),
            'programcoordinator2': request.POST.get("programcoordinator2"),
            'resourceperson': request.POST.get("resourceperson"),
            'designation': request.POST.get("designation"),
            'phone': request.POST.get("phone"),
            'mailid': request.POST.get("mailid"),

        }


#----------------------------------------------all activities above this line-------------------------------------------------------------
    proofs = [f for f in proofs if f]  # filter None values
    merged_file_field = None
    if proofs:
        buf = io.BytesIO()
        merge_uploads_to_pdf(proofs, buf)   # 👈 function implement pannano
        buf.seek(0)
        merged_file_field = ContentFile(buf.read(), name=f"{activityName}_{request.user.id}.pdf")
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