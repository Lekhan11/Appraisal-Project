import calendar
from urllib import request
from django.http import FileResponse, Http404
from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import *
import io,os
from django.core.files.base import ContentFile
from .utils import merge_uploads_to_pdf
from datetime import datetime
from django.conf import settings
from django.core.paginator import Paginator



def Login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid Username or password')
            return render(request, 'login.html')

    return render(request, 'login.html')

@login_required(login_url='login')
def Home(request, content=None):
    departments = Department.objects.all()
    activities = Activities.objects.all()
    acadYear = f"Jan {datetime.now().year} - Dec {datetime.now().year}"
    months = [calendar.month_name[i] for i in range(1, 13)]
    department = request.POST.get('department')
    month = request.POST.get('month')
    activityName = None
    submitted = False
    print("Content in Home:", repr(content))
    

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
        activities_submitted_this_month = ActivitySubmission.objects.filter(user__department=request.user.department, created_at__month=datetime.now().month).count()
        activities_submitted_this_year = ActivitySubmission.objects.filter(user__department=request.user.department, created_at__year=datetime.now().year).count()
        try:
            #activities_submitted_today = None
            activities_submitted_today = ActivitySubmission.objects.filter(user__department=request.user.department, created_at__date=datetime.now().date()).order_by('-created_at')
            paginator = Paginator(activities_submitted_today, 5)  # 10 per page
            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)
                # print(activities_submitted_today)        
        except ActivitySubmission.DoesNotExist:
            activities_submitted_today = None
        return render(request, 'hod/home.html',
                      {'user': request.user,
                       'totalFaculty': totalFaculty,
                       'activities_submitted_this_month': activities_submitted_this_month,
                       'activities_submitted_this_year': activities_submitted_this_year,
                    #    'activities_submitted_today': activities_submitted_today,
                       'acadYear': acadYear,
                       'page_obj': page_obj})

    elif request.user.role == 'faculty':
        if content=='dashboard':
            yearly_submissions = ActivitySubmission.objects.filter(user=request.user, created_at__year=datetime.now().year)
            monthly_submissions = ActivitySubmission.objects.filter(user=request.user, created_at__month=datetime.now().month).order_by('-created_at')
            paginator = Paginator(monthly_submissions, 5)  # 10 per page
            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)
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
                'content': content,
                'monthly_submissions': monthly_submissions if content=='dashboard' else None,
                'yearly_submissions': yearly_submissions if content=='dashboard' else None,
                'page_obj': page_obj if content=='dashboard' else None,
                
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
            'first_Year_Percent': request.POST.get("firstYear"),
            'second_Year_Percent': request.POST.get("secondYear"),
            'third_Year_Percent': request.POST.get("thirdYear"),
            'fourth_Year_Percent': request.POST.get("fourthYear"),
            'iae_Detail': request.POST.get("iaeDetail"),
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
            'first_Year': request.POST.get("firstYear"),
            'second_Year': request.POST.get("secondYear"),
            'third_Year': request.POST.get("thirdYear"),
            'fourth_Year': request.POST.get("fourthYear"),
        }

# Activite name 5
    elif activityName == "5":
        proofs = [
            request.FILES.get("attachproof1"),
            request.FILES.get("attachproof2"),
            request.FILES.get("attachproof3")
        ]
        details = {
            'guest_name': request.POST.get("guestname"),
            'event_title': request.POST.get("eventtitle"),
            'date': request.POST.get("date"),
            'participants': request.POST.get("participants"),
            'Coordinator_1': request.POST.get("Coordinator1"),
            'Coordinator_2': request.POST.get("Coordinator2"),
            'resource_name': request.POST.get("resourcename"),
            'organization_name': request.POST.get("organizationname"),
            'phone_number': request.POST.get("phonenumber"),
            'email': request.POST.get("email"),
        }

# Activite name 6
    elif activityName == "6":
        proofs = [
            request.FILES.get("attachproof1"),
            request.FILES.get("attachproof2"),
        ]
        details = {
            'faculty_name': request.POST.get("facultyname"),
            'event_type': request.POST.get("eventtype"),
            'mode': request.POST.get("mode"),
            'event_title': request.POST.get("eventitle"),
            'from_date': request.POST.get("fromdate"),
            'to_date': request.POST.get("todate"),
            'organizer_name': request.POST.get("organizername"),
        }

# Activite name 7
    elif activityName == "7":
        proofs = [
            request.FILES.get("attachproof1"),
            request.FILES.get("attachproof2"),
            request.FILES.get("attachproof3")
        ]
        details = {
            'title': request.POST.get("title"),
            'from_date': request.POST.get("fromdate"),
            'to_date': request.POST.get("todate"),
            'participants': request.POST.get("participants"),
            'Coordinator_1': request.POST.get("Coordinator1"),
            'Coordinator_2': request.POST.get("Coordinator2"),
            'resource_name': request.POST.get("resourcename"),
            'organization_name': request.POST.get("organizationname"),
            'phone_number': request.POST.get("phonenumber"),
            'email': request.POST.get("email"),
        }

# Activite name 8
    elif activityName == "8":
        proofs = [
            request.FILES.get("attachproof1"),
            request.FILES.get("attachproof2"),
            request.FILES.get("attachproof3")
        ]
        details = {
            'club_name': request.POST.get("clubname"),
            'title': request.POST.get("title"),
            'from_date': request.POST.get("fromdate"),
            'to_date': request.POST.get("todate"),
            'participants': request.POST.get("participants"),
            'Coordinator_1': request.POST.get("Coordinator1"),
            'Coordinator_2': request.POST.get("Coordinator2"),
            'resource_name': request.POST.get("resourcename"),
            'organization_name': request.POST.get("organizationname"),
            'phone_number': request.POST.get("phonenumber"),
            'email': request.POST.get("email"),
        }

# Activite name 9
    elif activityName == "9":
        proofs = [
            request.FILES.get("attachproof1"),
            request.FILES.get("attachproof2")
        ]
        details = {
            'student_name': request.POST.get("studentname"),
            'faculty_name': request.POST.get("facultyname"),
            'course_title': request.POST.get("coursetitle"),
            'from_date': request.POST.get("fromdate"),
            'to_date': request.POST.get("todate"),
            'mentor_name': request.POST.get("mentorname"),
        }

# Activite name 10
    elif activityName == "10":
        proofs = [
            request.FILES.get("attachproof1"),
            request.FILES.get("attachproof2")
        ]
        details = {
            'studentname': request.POST.get("studentname"),
            'facultyname': request.POST.get("facultyname"),
            'coursetitle': request.POST.get("coursetitle"),
            'fromdate': request.POST.get("fromdate"),
            'todate': request.POST.get("todate"),
            'mentorname': request.POST.get("mentorname"),
        }

# Activite name 11
    elif activityName == "11":
        proofs = [
            request.FILES.get("attachproof1"),
        ]
        details = {
            'granttitle': request.POST.get("granttitle"),
            'fundapplied': request.POST.get("fundapplied"),
            'agencyname': request.POST.get("agencyname"),
            'fundreceived': request.POST.get("fundreceived"),
            'date': request.POST.get("date"),
            'researchduration': request.POST.get("researchduration"),
        }

# Activite name 12
    elif activityName == "12":
        proofs = [
            request.FILES.get("attachproof1"),
        ]
        details = {
            'title': request.POST.get("title"),
            'agencyname': request.POST.get("agencyname"),
            'facultyname': request.POST.get("facultyname"),
            'fundapplied': request.POST.get("fundapplied"),
            'fundreceived': request.POST.get("fundreceived"),
            'fromdate': request.POST.get("fromdate"),
            'todate': request.POST.get("todate"),
            'studentsattended': request.POST.get("studentsattended"),
            'facultyattended': request.POST.get("facultyattended"),
        }

# Activite name 13
    elif activityName == "13":
        proofs = [
            request.FILES.get("attachproof1"),
            request.FILES.get("attachproof2"),
            request.FILES.get("attachproof3")
        ]
        details = {
            'facultyname': request.POST.get("facultyname"),
            'studentname': request.POST.get("studentname"),
            'presentationtitle': request.POST.get("presentationtitle"),
            'conferenceTitle': request.POST.get("conferenceTitle"),
            'conferencePlace': request.POST.get("conferencePlace"),
            'conferenceDate': request.POST.get("conferenceDate"),
            'issnNo': request.POST.get("issnNo"),
        }

# Activite name 14
    elif activityName == "14":
        proofs = [
            request.FILES.get("attachproof1"),
        ]
        details = {
            'facultyname': request.POST.get("facultyname"),
            'title': request.POST.get("title"),
            'journalName': request.POST.get("journalName"),
            'volumeNo': request.POST.get("volumeNo"),
            'issnNo': request.POST.get("issnNo"),
            'JournalLevel': request.POST.get("JournalLevel"),
            'websiteUrl': request.POST.get("websiteUrl"),
            'doiLink': request.POST.get("doiLink"),
            'hIndex': request.POST.get("hIndex"),
        }


#industrialguestlecture
    elif activityName == "15":  
        proofs = [
            request.FILES.get("attachproof1"),  # Word copy
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
        request.FILES.get("attachproof1"),
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
        return render(request, 'faculty/home.html', {'activitySubmitted': True, 'activityName': activityName ,'content':'activity'})
    except Exception as e:
        messages.error(request, 'There was an error submitting your activity. Please try again.')
        print(e)
        return render(request, 'faculty/home.html', {'activitySubmitted': True, 'error': True, 'content':'activity'})
    

def serve_pdf(request, filename):
    filepath = os.path.join(settings.MEDIA_ROOT, 'proofs', filename) # Adjust path as needed
    if not os.path.exists(filepath):
        raise Http404("PDF file not found.")
    
    return FileResponse(open(filepath, 'rb'), content_type='application/pdf')