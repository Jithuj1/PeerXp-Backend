from rest_framework import serializers
from .models import CustomUser, CustomAdmin, Department, Ticket
from django.contrib.auth.hashers import make_password


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = "__all__"

    def create(self, validated_data):
        password = validated_data.pop('password',None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance


class ReadUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id', 'name', 'phone', 'email', 'department', 'created_by', 'is_active', 'is_admin')
        depth = 1


class AdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomAdmin
        fields = "__all__"

    def create(self, validated_data):
        password = validated_data.pop('password',None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.password = make_password(password)
            instance.is_admin = True
        instance.save()
        return instance
    

class ReadAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomAdmin
        fields = ('id', 'name', 'phone', 'email', 'is_admin')


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = "__all__"


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ('subject', 'body', 'priority', 'user')


class TicketReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = "__all__"
        depth=1