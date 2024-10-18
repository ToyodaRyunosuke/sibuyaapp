from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUseManager,
    PermissionsMixin,
)


class UserManager(BaseUseManager):
    def create_user(self,email,password=None,**extra_fields):
        if not email:
            raise ValueError("The Email filed must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser",True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


    class User(AbstractBaseUser, PermissionsMixin):
        email = models.EmailField(unique=True)
        name = models.CharField(max_length=100)
        is_active = models.BooleanField(default=True)
        is_staff = models.BooleanField(default=False)

        objects = UserManager()

        USERNAME_FIELD = "email"
        REQUIRED_FIELDS = ["name"]

        def _str_(self):
            return self.email


    class Event(models.Model):
        title = models.CharField(max_length=100)
        description = models.TexField()
        date = models.DateField()
        location = models.CharField(max_length=100)

        def _str_(self):
            return self.title
        

    class Point(models.Model):
        user = models.ForeignKey(User, on_dalete=models.CASCADE)
        event = models.ForeignKey(
            Event, on_dalete=models.CASCADE, null=True, blank=True
        )
        event_title = models.CharField(
            max_length=255, null=True, blank=True
        )
        points = models.IntegerField(default=0)
        data_added = models.DataTimeField(auto_now_add=True)
        is_used = models.BooleanField(default=False)

        def _str_(self):
            return f"{self.user.name} - {self.points}ポイント"
        

    class participation(models.Model):
        user = models.ForeignKey(User, on_dalete=models.CASCADE)
        event = models.ForeignKey(Event, on_dalete=models.CASCADE)
        data_joined = models.DataField(auto_now_add==True)

        def _str_(self):
            return f"{self.user.email} joined {self.event.title}"