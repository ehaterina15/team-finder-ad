from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_GET
from .forms import RegisterForm, LoginForm, EditProfileForm, ChangePasswordForm
from .models import User, Skill
from django.core.paginator import Paginator


def register(request):
    form = RegisterForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)
        return redirect('projects:list')
    return render(request, 'users/register.html', {'form': form})


def user_login(request):
    form = LoginForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = authenticate(
            request,
            username=form.cleaned_data['email'],
            password=form.cleaned_data['password']
        )
        if user:
            login(request, user)
            return redirect('projects:list')
        form.add_error(None, 'Неверный имейл или пароль')
    return render(request, 'users/login.html', {'form': form})


def user_logout(request):
    logout(request)
    return redirect('projects:list')


def user_detail(request, pk):
    user = get_object_or_404(User, pk=pk)
    return render(request, 'users/user-details.html', {'user': user})


def users_list(request):
    skill_name = request.GET.get('skill', '').strip()
    all_skills = Skill.objects.all()
    participants_qs = User.objects.all().order_by('id')
    active_skill = None

    if skill_name:
        participants_qs = participants_qs.filter(skills__name=skill_name)
        active_skill = skill_name

    paginator = Paginator(participants_qs, 12)
    page = request.GET.get('page')
    page_obj = paginator.get_page(page)

    return render(request, 'users/participants.html', {
        'page_obj': page_obj,        # было participants, теперь page_obj
        'all_skills': all_skills,
        'active_skill': active_skill,
    })


@login_required
def edit_profile(request, pk=None):
    form = EditProfileForm(request.POST or None, request.FILES or None, instance=request.user)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('users:detail', pk=request.user.pk)
    return render(request, 'users/edit_profile.html', {'form': form})

@login_required
def change_password(request):
    form = ChangePasswordForm(request.user, request.POST or None)
    if request.method == 'POST' and form.is_valid():
        request.user.set_password(form.cleaned_data['new_password1'])
        request.user.save()
        login(request, request.user)
        return redirect('users:detail', pk=request.user.pk)
    return render(request, 'users/change_password.html', {'form': form})


@require_GET
def skills_autocomplete(request):
    q = request.GET.get('q', '')
    skills = Skill.objects.filter(name__istartswith=q)[:10]
    data = [{'id': s.pk, 'name': s.name} for s in skills]
    return JsonResponse(data, safe=False)


@login_required
@require_POST
def skill_add(request, pk):
    import json
    user = get_object_or_404(User, pk=pk)
    if request.user != user:
        return JsonResponse({'error': 'Нет доступа'}, status=403)

    # пробуем получить из JSON тела
    try:
        data = json.loads(request.body)
    except Exception:
        data = request.POST

    skill_id = data.get('skill_id')
    name     = data.get('name')
    created  = False

    if skill_id:
        skill = get_object_or_404(Skill, pk=skill_id)
    elif name:
        skill, created = Skill.objects.get_or_create(name=name)
    else:
        return JsonResponse({'error': 'Нет данных'}, status=400)

    added = False
    if skill not in user.skills.all():
        user.skills.add(skill)
        added = True
    return JsonResponse({'skill_id': skill.pk, 'name': skill.name, 'created': created, 'added': added})

@login_required
@require_POST
def skill_remove(request, pk, skill_pk):
    user  = get_object_or_404(User, pk=pk)
    skill = get_object_or_404(Skill, pk=skill_pk)

    if request.user != user:
        return JsonResponse({'error': 'Нет доступа'}, status=403)

    user.skills.remove(skill)
    return JsonResponse({'status': 'ok'})