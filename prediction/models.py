from django.db import models

# Create your models here.

class Suburb(models.Model):
    suburb_code = models.IntegerField(primary_key=True)
    suburb_name = models.CharField(max_length=30)
    train_station = models.IntegerField()
    bus_station = models.IntegerField()
    hospitals = models.IntegerField()
    schools = models.IntegerField()
    restaurants = models.IntegerField()
    shopping_center = models.IntegerField()
    park  = models.IntegerField()
    sub_lat  = models.FloatField()
    sub_long  = models.FloatField()

    def __str__(self):
        return self.suburb_name

