import json

from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET, require_POST

from .forms import LoginForm, ProfileEditForm, RegisterForm, UserPasswordChangeForm
from .models import Skill, User
from .pagination import paginate

USER_LIST_PAGE_SIZE = 12


def register(request):
    form = RegisterForm(request.POST or None)
    if form.is_valid():
        user = form.save()
        login(request, user)
        return redirect('projects:list')
    return render(request, 'users/register.html', {'form': form})


def user_login(request):
    form = LoginForm(request.POST or None)
    if form.is_valid():
        user = authenticate(
            request,
            username=form.cleaned_data['email'],
            password=form.cleaned_data['password'],
        )
        if user:
            login(request, user)
            return redirect('projects:list')
        form.add_error(None, 'Неверный имейл или пароль')
    return render(request, 'users/login.html', {'form': form})


def user_logout(request):
    logout(request)
    return redirect('projects:list')


def user_detail(request, user_id):
    profile_user = get_object_or_404(User, pk=user_id)
    return render(request, 'users/user-details.html', {'user': profile_user})


def users_list(request):
    skill_name = request.GET.get('skill', '').strip()
    all_skills = Skill.objects.all()
    qs = User.objects.all()
    active_skill = None

    if skill_name:
        qs = qs.filter(skills__name=skill_name)
        active_skill = skill_name

    page_obj = paginate(request, qs, USER_LIST_PAGE_SIZE)

    return render(request, 'users/participants.html', {
        'page_obj': page_obj,
        'all_skills': all_skills,
        'active_skill': active_skill,
    })


@login_required
def edit_profile(request):
    form = ProfileEditForm(
        request.POST or None,
        request.FILES or None,
        instance=request.user,
    )
    if form.is_valid():
        form.save()
        return redirect('users:detail', user_id=request.user.pk)
    return render(request, 'users/edit_profile.html', {'form': form, 'user': request.user})


@login_required
def change_password(request):
    form = UserPasswordChangeForm(request.user, request.POST or None)
    if form.is_valid():
        form.save()
        update_session_auth_hash(request, form.user)
        return redirect('users:detail', user_id=request.user.pk)
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
    user = get_object_or_404(User, pk=pk)
    if request.user != user:
        return JsonResponse({'error': 'Нет доступа'}, status=403)

    try:
        data = json.loads(request.body)
    except Exception:
        data = request.POST

    skill_id = data.get('skill_id')
    name = data.get('name')
    created = False

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

    return JsonResponse({
        'skill_id': skill.pk,
        'name': skill.name,
        'created': created,
        'added': added,
    })


@login_required
@require_POST
def skill_remove(request, pk, skill_pk):
    user = get_object_or_404(User, pk=pk)
    skill = get_object_or_404(Skill, pk=skill_pk)

    if request.user != user:
        return JsonResponse({'error': 'Нет доступа'}, status=403)

    user.skills.remove(skill)
    return JsonResponse({'status': 'ok'})