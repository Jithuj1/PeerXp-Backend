from django.urls import path
from .views import *

urlpatterns = [
    path('admins', AdminDetails),
    path('admins/<int:id>', CurdAdmin),
    path('admins/auth', AuthAdmin),
    path('department', DepartmentDetails),
    path('department/<int:id>', CrudDepartment),
    path('users', UsersDetails),
    path('users/<int:id>', CrudUser),
    path('users/auth', AuthUser),
    path('ticket', TicketDetails),
    path('ticket/<int:id>', CrudTicket),
    path('zendesk_ticket', CreateZendeskTicket),
]