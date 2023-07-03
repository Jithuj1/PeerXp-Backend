from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser


class MyAccountManager(BaseUserManager):
    def create_user(self, email, name, phone, password=None, **kwargs):
        if not email:
            raise ValueError('User must have an email')
        
        if not phone:
            raise ValueError('User must have a phone number')
        
        email = self.normalize_email(email)
        user = self.model(
            email=email,
            name=name,
            phone = phone,
            **kwargs
        )

        user.set_password(password)
        user.save(using=self._db)
        
        return user
    
    def create_superuser(self, email, name, phone, password, **kwargs):
        kwargs.setdefault('is_staff', True)
        kwargs.setdefault('is_superuser', True)

        return self.create_user(email, name, phone, password, **kwargs)


class CustomUser(AbstractBaseUser):
    name = models.CharField(max_length=50)
    email = models.EmailField(max_length=254, unique=True, null=False)
    phone = models.CharField(max_length=50)
    password = models.TextField(max_length=50)

    department = models.ForeignKey("Mainapp.Department", on_delete=models.CASCADE)
    created_by =models.ForeignKey("Mainapp.CustomAdmin", on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateField(auto_now=True)
    is_admin  = models.BooleanField(default=False)
    is_active   = models.BooleanField(default=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS =['name', 'phone']
    
    objects = MyAccountManager()

    def __str__(self):
        return self.name

    def has_perm(self, perm, obj=None):
        return self.is_admin
    
    def has_module_perms(self, add_label):
        return True


class CustomAdmin(models.Model):
    name = models.CharField(max_length=50)
    email = models.EmailField(max_length=254, unique=True, null=False)
    phone = models.CharField(max_length=50, unique=True, null=False)
    password = models.TextField(max_length=50)

    created_at = models.DateTimeField(auto_now=True)
    is_admin  = models.BooleanField(default=True)
    is_active   = models.BooleanField(default=True)
    

class Department(models.Model):
    dept_name = models.CharField(max_length=50)
    dept_description = models.CharField(max_length=50)
    created_by = models.ForeignKey("Mainapp.CustomAdmin", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    def has_users(self):
        return CustomUser.objects.filter(department=self).exists()

    def delete(self, *args, **kwargs):
        if self.has_users():
            raise Exception("Cannot delete department with associated users.")
        super().delete(*args, **kwargs)


class Ticket(models.Model):
    subject = models.CharField(max_length=50)
    body = models.TextField()
    priority = models.CharField(max_length=50)
    user_email = models.EmailField(max_length=254)
    user_phone = models.CharField(max_length=50)
    user = models.ForeignKey("Mainapp.CustomUser", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now=True)