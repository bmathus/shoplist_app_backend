from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

class UserManager(BaseUserManager):
    def create_user(self, email,name, password=None):
        if not email:
            raise ValueError('Users must have an email address')
        if not name:
            raise ValueError('Users must have an name')

        user = self.model(
            email=self.normalize_email(email),
            name=name
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email,name,password):
        user = self.create_user(
            email,
            password=password,
            name=name
        )
        user.save(using=self._db)
        return user

class List(models.Model):
    name = models.TextField()
    num_ppl = models.IntegerField(default=1)
    num_items = models.IntegerField(default=0)
    invite_code = models.TextField(unique=True)
    
    class Meta:
        db_table = "shopping_lists"

    def json(self):
        return {
            'id':self.id,
            'name':self.name,
            'num_ppl':self.num_ppl,
            'num_items':self.num_items,
            'invite_code':self.invite_code
        }

class User(AbstractBaseUser):
    name = models.CharField(max_length=20, default='Anonymous')
    email = models.EmailField(max_length=50, unique=True)
    user_lists = models.ManyToManyField(List,db_table="user_lists")

    username = None
    last_login = None
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ["name"]
    class Meta:
        db_table = 'users' 

    objects = UserManager()

    def json(self):
        return {
            'id':self.id,
            'name':self.name,
            'email':self.email, 
        }

class Product(models.Model):
    list = models.ForeignKey(List, on_delete=models.CASCADE)
    name = models.CharField(max_length=20)
    quantity = models.FloatField(null=True)
    unit = models.TextField(null=True)
    bought = models.BooleanField(default=False)

    class Meta:
        db_table = 'products' 

    def json(self):
        return {
            'id':self.id,
            'name':self.name,
            'quantity':self.quantity,
            'unit':self.unit,
            'bought':self.bought
        }



