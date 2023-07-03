from .models import *
from .serializer import *
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes
import jwt
from datetime import datetime, timedelta
from django.conf import settings
from django.contrib.auth.hashers import check_password
from datetime import datetime
import requests
import json


def Validate_JWT(request):
    try:
        token = request.headers.get('Authorization').split(' ')[1]
    except:
        return False
    token = token.strip('"')
    current_time = datetime.utcnow().timestamp()
    try:
        print('payload is this', token)
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        print('payload is this', payload)
        if payload['exp'] < current_time:
            return False
        else:
            data = {
                "user_id": payload['user_id'],
                "is_admin": payload['is_admin']}
            return data

    except jwt.ExpiredSignatureError:
        print('singnature')
        return False
    except jwt.InvalidTokenError:
        print('invalied')
        return False


@api_view(['GET', 'POST'])
def AdminDetails(request):
    if request.method == "POST":
        email = request.data.get('email')
        phone = request.data.get('phone')
        email = email.lower()
        email_exist = CustomAdmin.objects.filter(email=email).exists()
        phone_exist = CustomAdmin.objects.filter(phone=phone).exists()
        if email_exist:
            return Response({'message': "Email already taken "}, status=status.HTTP_406_NOT_ACCEPTABLE)
        if phone_exist:
            return Response({"message": "Phone number already taken"}, status=status.HTTP_406_NOT_ACCEPTABLE)
        serializer = AdminSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            user = CustomAdmin.objects.get(email=email)
            serializer = ReadAdminSerializer(user)
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        else:
            return Response({'message': 'wrong credentials'})
    else:
        user = CustomAdmin.objects.all()
        serializer = ReadAdminSerializer(user, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
def AuthAdmin(request):
    if request.method == "POST":
        email_or_phone = request.data.get('email_or_phone')
        password = request.data.get('password')
        print(email_or_phone, password)
        try:
            user = CustomAdmin.objects.get(email=email_or_phone)
        except CustomAdmin.DoesNotExist:
            try:
                user = CustomAdmin.objects.get(phone=email_or_phone)
            except CustomAdmin.DoesNotExist:
                return Response({'error': 'Invalid credentials'}, status=400)
        expiration_time = datetime.utcnow() + timedelta(days=1)
        if check_password(password, user.password):
            payload = {
                'user_id': user.id,
                'is_admin': user.is_admin,
                'exp': expiration_time

            }
            token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
            print(token)
            return Response({'token': token}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid credentials'}, status=400)


@api_view(['GET'])
def CurdAdmin(request, id):
    print('here')
    try:
        admin = CustomAdmin.objects.get(id=id)
    except:
        data = {"message": "user not found"}
        return Response(data, status=status.HTTP_404_NOT_FOUND)
    serializer = AdminSerializer(admin)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST', 'GET'])
def DepartmentDetails(request):
    result = Validate_JWT(request)
    print(result)
    if result == False:
        return Response(status=status.HTTP_401_UNAUTHORIZED)
    if result['is_admin'] == False:
        return Response(status=status.HTTP_401_UNAUTHORIZED)
    if request.method == "GET":
        depts = Department.objects.all()
        serializer = DepartmentSerializer(depts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    else:
        serializer = DepartmentSerializer(data=request.data, partial=True)
        if serializer.is_valid():
            dept = serializer.save()
            serializer = DepartmentSerializer(dept)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid Details'}, status=status.HTTP_406_NOT_ACCEPTABLE)


@api_view(['GET', 'PUT', 'DELETE'])
def CrudDepartment(request, id):
    result = Validate_JWT(request)
    if not result:
        return Response(status=status.HTTP_401_UNAUTHORIZED)
    try:
        dept = Department.objects.get(id=id)
    except:
        data = {"message": "user not found"}
        return Response(data, status=status.HTTP_404_NOT_FOUND)
    if request.method == "GET":
        serializer = DepartmentSerializer(dept)
        return Response(serializer.data, status=status.HTTP_200_OK)
    elif request.method == "PUT":
        serializer = DepartmentSerializer(
            dept, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            updated_user = Department.objects.get(id=id)
            serializer = DepartmentSerializer(updated_user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({'message': 'invalid input'}, status=status.HTTP_406_NOT_ACCEPTABLE)
    else:
        dept.delete()
        return Response(status=status.HTTP_200_OK)


@api_view(['GET', 'POST'])
def UsersDetails(request):
    result = Validate_JWT(request)
    if not result:
        return Response(status=status.HTTP_401_UNAUTHORIZED)
    if request.method == "POST":
        email = request.data.get('email')
        phone = request.data.get('phone')
        email = email.lower()
        email_exist = CustomUser.objects.filter(email=email).exists()
        phone_exist = CustomUser.objects.filter(phone=phone).exists()
        if email_exist:
            return Response({'message': "Email already taken "}, status=status.HTTP_406_NOT_ACCEPTABLE)
        if phone_exist:
            return Response({"message": "Phone number already taken"}, status=status.HTTP_406_NOT_ACCEPTABLE)
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            user = CustomUser.objects.get(email=email)
            serializer = ReadUserSerializer(user)
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        else:
            return Response({'message': 'wrong credentials'})
    else:
        user = CustomUser.objects.all()
        serializer = ReadUserSerializer(user, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET', 'PUT', 'DELETE'])
def CrudUser(request, id):
    try:
        user = CustomUser.objects.get(id=id)
    except:
        data = {"message": "user not found"}
        return Response(data, status=status.HTTP_404_NOT_FOUND)
    if request.method == "GET":
        serializer = ReadUserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    elif request.method == "PUT":
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            updated_user = CustomUser.objects.get(id=id)
            serializer = ReadUserSerializer(updated_user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({'message': 'invalid input'}, status=status.HTTP_406_NOT_ACCEPTABLE)
    else:
        user.delete()
        return Response(status=status.HTTP_200_OK)


@api_view(['POST'])
def AuthUser(request):
    if request.method == "POST":
        print('here it is')
        email_or_phone = request.data.get('email_or_phone')
        password = request.data.get('password')
        print(email_or_phone, password)
        try:
            user = CustomUser.objects.get(email=email_or_phone)
        except CustomUser.DoesNotExist:
            try:
                user = CustomUser.objects.get(phone=email_or_phone)
                print('here')
            except CustomUser.DoesNotExist:
                return Response({'error': 'Invalid credentials'}, status=400)
        expiration_time = datetime.utcnow() + timedelta(days=1)
        if check_password(password, user.password):
            print('here')
            payload = {
                'user_id': user.id,
                'is_admin': user.is_admin,
                'exp': expiration_time
            }
            token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
            return Response({'token': token})
        else:
            return Response({'error': 'Invalid credentials'}, status=400)


def CreateZendeskTicket(subject, body, priority):
    url = "https://brototype1947.zendesk.com/api/v2/tickets"

    api_token = "MiigcO1wCgr0LicdYlQcx82aK12sG65mkNzJs2nK"

    # second = "oeEFftLhkVmtDpakrcZ8DhFuRvA4e3hHwov2eEaz"

    username = "jithujacob73@gmail.com"

    payload = {
        "ticket": {
            "comment": {
                "body": body
            },
            "priority":priority,
            "subject": subject
        }
    }

    # headers = {
    #     "Authorization": "Bearer {}".format(api_token)
    # }
    
    headers = {
        "Content-Type": "application/json",
    }

    response = requests.request(
        "POST",
        url,
        auth=(username, api_token),
        headers=headers,
        json=payload
    )
    print(response)
    if response.status_code == 201:
        return response.json()
    else:
        return None


def DeleteZendeskTicket(id):
    url = "https://brototype1947.zendesk.com/api/v2/tickets/{id}"

    api_token = "MiigcO1wCgr0LicdYlQcx82aK12sG65mkNzJs2nK"
    # I created this api token from zendesk Add Api Token but when I use this token response shows that invalid token
    # or could not authenticate you. And I tried many ways to interact with this api. I don't know how it's works

    username = "jithujacob73@gmail.com"

    headers = {
        "Content-Type": "application/json",
    }

    response = requests.request(
        "DELETE",
        url,
        auth=(username, api_token),
        headers=headers
    )

    if response.status_code == 200:
        return response.json()
    else:
        return None


@api_view(['GET', 'POST'])
def TicketDetails(request):
    result = Validate_JWT(request)
    if result == False:
        print('here')
        return Response(status=status.HTTP_401_UNAUTHORIZED)
    if request.method == "POST":
        serializer = TicketSerializer(data=request.data)
        if serializer.is_valid():
            ticket = serializer.save()
            user_id = ticket.user_id
            user = CustomUser.objects.get(id=user_id)
            ticket.user_email = user.email
            ticket.user_phone = user.phone
            ticket.save()
            ticket_subject = ticket.subject
            ticket_body = ticket.body
            ticket_priority = ticket.priority
            online_ticket = CreateZendeskTicket(ticket_subject, ticket_body, ticket_priority)
            serializer = TicketReadSerializer(ticket)
            # if online_ticket:
            #     message = {"message": "online ticket issued for user"}
            # else:
            #     message = {"message": "online ticket is not issued"}
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        else:
            return Response({'message': 'wrong credentials'})
    else:
        if result['is_admin'] == True:
            ticket = Ticket.objects.all()
            serializer = TicketReadSerializer(ticket, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            user_id = result['user_id']
            ticket = Ticket.objects.filter(user=user_id)
            serializer = TicketReadSerializer(ticket, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['DELETE'])
def CrudTicket(request, id):
    print('reached crud')
    result = Validate_JWT(request)
    if not result:
        return Response(status=status.HTTP_401_UNAUTHORIZED)
    try:
        ticket = Ticket.objects.get(id=id)
    except:
        data = {"message": "No ticket issued"}
        return Response(data, status=status.HTTP_404_NOT_FOUND)
    if result['is_admin'] == True:
        ticket.delete()
        online_ticket_id = ""
        DeleteZendeskTicket(online_ticket_id)
        return Response(status=status.HTTP_200_OK)
    elif ticket.user_id == result['user_id']:
        ticket.delete()
        return Response(status=status.HTTP_200_OK)
    else:
        print('un autheriserd')
        return Response(status=status.HTTP_401_UNAUTHORIZED)
