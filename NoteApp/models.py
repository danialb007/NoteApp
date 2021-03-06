from django.db import models

class Users(models.Model):
    user = models.CharField(max_length=16)
    email = models.EmailField(default='None')
    passwd = models.CharField(max_length=16)
    def __str__(self):
        return self.user + " email: " + self.email

class Notes(models.Model):
    user = models.CharField(max_length=16,unique=False)
    notes = models.TextField()
    def __str__(self):
        return self.notes