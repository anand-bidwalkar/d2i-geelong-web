from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from import_export import resources, fields
from .models import Suburb

class SuburbResource(resources.ModelResource):

    suburb_name = fields.Field(
    column_name ="Suburb",
    attribute='suburb_name',
    
    )

    suburb_code = fields.Field(
    column_name ="Suburb_Code",
    attribute='suburb_code',
    
    )

    train_station = fields.Field(
    column_name ="Train Station",
    attribute='train_station',
    
    )

    bus_station = fields.Field(
    column_name ="Bus Station",
    attribute='bus_station',
    
    )

    shopping_center = fields.Field(
    column_name ="Shopping Center",
    attribute='shopping_center',
    
    )

    hospitals = fields.Field(
    column_name ="Hospitals",
    attribute='hospitals',
    
    )

    schools = fields.Field(
    column_name ="Schools",
    attribute='schools',
    
    )

    park = fields.Field(
    column_name ="Park",
    attribute='park',
    
    )

    restaurants = fields.Field(
    column_name ="Restaurants",
    attribute='restaurants',
    
    )

    sub_lat = fields.Field(
    column_name ="Sub_Lat",
    attribute='sub_lat',
    
    )

    sub_long = fields.Field(
    column_name ="Sub_Long",
    attribute='sub_long',
    
    )
    class Meta:
        model = Suburb
        exclude = ('id',)
        export_order = ('suburb_name', 'suburb_code','train_station','bus_station','hospitals','schools','restaurants','shopping_center','park','sub_lat','sub_long')
        import_id_fields = ('suburb_name', 'suburb_code','train_station','bus_station','hospitals','schools','restaurants','shopping_center','park','sub_lat','sub_long')

@admin.register(Suburb)
class SuburbAdmin(ImportExportModelAdmin):
    resource_class = SuburbResource








# Register your models here.
