import json
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import authenticate, login
from .models import Incident, AnonymousReport
from .models import Profile
from .forms import IncidentForm, UserRegisterForm, AnonymousReportForm

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Регистрация успешна!')
            return redirect('map')
    else:
        form = UserRegisterForm()
    return render(request, 'incidents/register.html', {'form': form})

def map_view(request):
    incidents = Incident.objects.filter(status='confirmed')
    incidents_list = []
    for inc in incidents:
        incidents_list.append({
            'id': inc.id,
            'lat': inc.latitude,
            'lng': inc.longitude,
            'type': inc.category,
            'title': inc.title,
            'place': getattr(inc, 'place', 'координаты'),
            'date': inc.date_occurred.strftime('%Y-%m-%d'),
            'desc': inc.description,
        })
    reports = AnonymousReport.objects.all().order_by('-created_at')[:20]
    reports_list = [{
        'type': 'Сообщение',
        'place': r.location,
        'description': r.message,
        'createdAt': r.created_at.isoformat(),
    } for r in reports]
    form = AnonymousReportForm()
    context = {
        'incidents_json': json.dumps(incidents_list, ensure_ascii=False),
        'anonymous_reports_json': json.dumps(reports_list, ensure_ascii=False),
        'anonymous_form': form,
    }
    return render(request, 'incidents/map.html', context)

@login_required
def add_incident(request):
    if request.method == 'POST':
        form = IncidentForm(request.POST)
        if form.is_valid():
            incident = form.save(commit=False)
            incident.created_by = request.user
            incident.status = 'new'
            incident.save()
            messages.success(request, 'Происшествие добавлено и отправлено на модерацию.')
            return redirect('map')
    else:
        form = IncidentForm()
    return render(request, 'incidents/add_incident.html', {'form': form})

def anonymous_report(request):
    if request.method == 'POST':
        form = AnonymousReportForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Ваше анонимное сообщение принято. Спасибо!')
            return redirect('map')
    else:
        form = AnonymousReportForm()
    return render(request, 'incidents/anonymous_report.html', {'form': form})

from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Incident, AnonymousReport, Profile

@login_required

@login_required
def profile_data(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    incident_count = profile.get_incident_count()
    data = {
        'username': request.user.username,
        'email': request.user.email,
        'rating': profile.rating,
        'incident_count': incident_count,
        'bio': profile.bio,
        'avatar': profile.avatar.url if profile.avatar else None,
        'date_joined': request.user.date_joined.strftime('%d.%m.%Y'),
    }
    return JsonResponse(data)

def ajax_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return JsonResponse({'success': True, 'username': user.username})
        else:
            return JsonResponse({'success': False, 'error': 'Неверное имя пользователя или пароль.'})
    return JsonResponse({'success': False, 'error': 'Метод не разрешён.'})

def ajax_register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        if password != password2:
            return JsonResponse({'success': False, 'error': 'Пароли не совпадают.'})
        if User.objects.filter(username=username).exists():
            return JsonResponse({'success': False, 'error': 'Имя пользователя уже занято.'})
        user = User.objects.create_user(username=username, email=email, password=password)
        login(request, user)
        return JsonResponse({'success': True, 'username': user.username})
    return JsonResponse({'success': False, 'error': 'Метод не разрешён.'})


from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse

@staff_member_required
def get_pending_count(request):
    count = Incident.objects.filter(status='new').count()
    return JsonResponse({'count': count})

@staff_member_required
def moderation_panel(request):
    incidents = Incident.objects.filter(status='new').order_by('-created_at')
    if request.method == 'POST':
        incident_id = request.POST.get('incident_id')
        action = request.POST.get('action')
        incident = Incident.objects.get(id=incident_id)
        if action == 'confirm':
            incident.status = 'confirmed'
            incident.save()
            # Начисляем рейтинг пользователю
            profile = incident.created_by.profile
            profile.rating += 10
            profile.save()
        elif action == 'reject':
            incident.status = 'rejected'
            incident.save()
        return JsonResponse({'success': True})
    return render(request, 'incidents/moderation.html', {'incidents': incidents})
