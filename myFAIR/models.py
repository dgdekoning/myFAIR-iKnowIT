from django.db import models
import views


class GalaxyServer(models.Model):
    api = models.CharField(max_length=32)
    location = models.CharField(max_length=254)
    name = models.CharField(max_length=254)