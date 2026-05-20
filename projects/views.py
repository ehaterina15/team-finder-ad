from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .constants import PROJECT_STATUS_CHOICES
from .forms import ProjectForm
from .models import Project
from .pagination import paginate

PAGE_SIZE = 12


def project_list(request):
    projects_qs = Project.objects.all()
    page_obj = paginate(request, projects_qs, PAGE_SIZE)
    return render(request, 'projects/project_list.html', {
        'page_obj': page_obj,
        'projects': projects_qs,
    })


def project_detail(request, pk):
    project = get_object_or_404(
        Project.objects.select_related('owner').prefetch_related('participants'),
        pk=pk,
    )
    return render(request, 'projects/project-details.html', {'project': project})


@login_required
def project_create(request):
    form = ProjectForm(request.POST or None)
    if form.is_valid():
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
    if form.is_valid():
        form.save()
        return redirect('projects:detail', pk=project.pk)
    return render(request, 'projects/create-project.html', {
        'form': form,
        'is_edit': True,
    })


@login_required
@require_POST
def project_complete(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if project.owner_id != request.user.pk or project.status != PROJECT_STATUS_CHOICES[0][0]:
        return JsonResponse(
            {'status': 'error', 'message': 'Недостаточно прав для этого действия'},
            status=403,
        )
    project.status = PROJECT_STATUS_CHOICES[1][0]
    project.save(update_fields=['status'])
    return JsonResponse({'status': 'ok', 'project_status': project.status})


@login_required
@require_POST
def toggle_participate(request, pk):
    project = get_object_or_404(Project, pk=pk)
    user = request.user
    if project.owner_id == user.pk:
        return JsonResponse(
            {'status': 'error', 'message': 'Автор проекта не может присоединиться как участник'},
            status=400,
        )
    if project.status != PROJECT_STATUS_CHOICES[0][0]:
        return JsonResponse(
            {'status': 'error', 'message': 'К проекту нельзя присоединиться: набор закрыт'},
            status=400,
        )
    participating = project.participants.filter(pk=user.pk).exists()
    if participating:
        project.participants.remove(user)
    else:
        project.participants.add(user)
    return JsonResponse({'status': 'ok', 'participating': not participating})