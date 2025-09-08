from django.db import models
from django.contrib.auth.models import User, AbstractUser
import uuid

OPCIONES_TIPO_CN = [
    ('Api', 'Api'),
    ('Server Sql', 'Server Sql'),
]

class Role(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    description = models.CharField(max_length=50, blank=True, null=True)
    avatar_role = models.TextField(blank=True)
    create = models.DateTimeField(auto_now_add=True, null=True)
    modified = models.DateTimeField(auto_now=True, null=True)
    
    def __str__(self):
        return self.description or "Sin descripción"

class Category(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    description = models.CharField(max_length=100, blank=True, null=True)
    avatar_category = models.TextField(blank=True)
    create = models.DateTimeField(auto_now_add=True, null=True)
    modified = models.DateTimeField(auto_now=True, null=True)
    
    def __str__(self):
        return self.description or "Sin descripción"
    
class Company(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ruc = models.CharField(max_length=12, unique=True)
    description = models.CharField(max_length=150, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    avatar_profile = models.TextField(blank=True)
    ip = models.CharField(max_length=255, null=True)
    puerto = models.CharField(max_length=255, default='1433', null=True)
    token = models.CharField(max_length=255, null=True)
    
    server = models.CharField(max_length=255, null=True)
    database = models.CharField(max_length=255, null=True)
    uid = models.CharField(max_length=255, null=True)
    uid_pass = models.CharField(max_length=255, null=True)
    driver = models.CharField(max_length=255, null=True, default='ODBC Driver 17 for SQL Server')
    type_con = models.CharField(max_length=50, choices=OPCIONES_TIPO_CN, default='Api', null=True)
    
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    create = models.DateTimeField(auto_now_add=True, null=True)
    modified = models.DateTimeField(auto_now=True, null=True)
    
    def __str__(self):
        return self.description or f"Compañía {self.ruc}"
    
class Profile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    surname = models.CharField(max_length=255)
    verified = models.BooleanField(default=False)
    requested_verified = models.BooleanField(default=False)
    avatar_profile = models.TextField(blank=True, help_text="Avatar en formato base64")
    phone = models.CharField(max_length=20, blank=True, null=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.CASCADE, null=True)
    create = models.DateTimeField(auto_now_add=True, null=True)
    modified = models.DateTimeField(auto_now=True, null=True)
    
    def __str__(self):
        return f"{self.surname} {self.name}"
    
    @property
    def avatar_url(self):
        """Retorna la URL del avatar para usar en templates"""
        if self.avatar_profile and self.avatar_profile.startswith('data:image'):
            return self.avatar_profile
        return None
    
    @property
    def initials(self):
        """Retorna las iniciales del usuario"""
        first_initial = self.name[0].upper() if self.name else ''
        last_initial = self.surname[0].upper() if self.surname else ''
        return f"{first_initial}{last_initial}" or self.user.username[0].upper()