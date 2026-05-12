from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Project
from .forms import ProjectForm


def project_list(request):
    projects_qs = Project.objects.all()
    paginator = Paginator(projects_qs, 12)
    page = request.GET.get('page')
    page_obj = paginator.get_page(page)
    return render(request, 'projects/project_list.html', {
        'page_obj': page_obj,
        'projects': projects_qs,  # для проверки {% if projects %} в шаблоне
    })


def project_detail(request, pk):
    project = get_object_or_404(Project, pk=pk)
    return render(request, 'projects/project-details.html', {'project': project})


@login_required
def project_create(request):
    form = ProjectForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        project = form.save(commit=False)
        project.owner = request.user
        project.save()
        project.participants.add(request.user)
        return redirect('projects:detail', pk=project.pk)
    return render(request, 'projects/create-project.html', {
        'form': form,
        'is_edit': False,
    })


@login_required
def project_edit(request, pk):
    project = get_object_or_404(Project, pk=pk, owner=request.user)
    form = ProjectForm(request.POST or None, instance=project)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('projects:detail', pk=project.pk)
    return render(request, 'projects/create-project.html', {
        'form': form,
        'is_edit': True,
    })


@login_required
@require_POST
def project_complete(request, pk):
    project = get_object_or_404(Project, pk=pk, owner=request.user)
    if project.status == 'open':
        project.status = 'closed'
        project.save()
    return JsonResponse({'status': 'ok', 'project_status': project.status})


@login_required
@require_POST
def toggle_participate(request, pk):
    project = get_object_or_404(Project, pk=pk)
    user = request.user
    if user in project.participants.all():
        project.participants.remove(user)
        participating = False
    else:
        project.participants.add(user)
        participating = True
    return JsonResponse({'status': 'ok', 'participating': participating})