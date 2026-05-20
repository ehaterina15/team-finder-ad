from django.urls import path

from . import views

app_name = 'users'

urlpatterns = [
    path('register/',                              views.register,            name='register'),
    path('login/',                                 views.user_login,          name='login'),
    path('logout/',                                views.user_logout,         name='logout'),
    path('list/',                                  views.users_list,          name='list'),
    path('edit-profile/',                          views.edit_profile,        name='edit_profile'),
    path('change-password/',                       views.change_password,     name='change_password'),
    path('<int:user_id>/',                         views.user_detail,         name='detail'),
    path('skills/',                                views.skills_autocomplete, name='skills_autocomplete'),
    path('<int:pk>/skills/add/',                   views.skill_add,           name='skill_add'),
    path('<int:pk>/skills/<int:skill_pk>/remove/', views.skill_remove,        name='skill_remove'),
]