from django.contrib import admin
from api.models import User, Sensor, SensorData



class UserAdmin(admin.ModelAdmin):
    list_display = [
        'email',
        'first_name',
        'last_name',
        'username',
        'company_name',
        'role'
    ]
    
    list_display_links = ['email']
    

admin.site.register(User, UserAdmin)


class SensorAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'operator',
        'description',
        'location',
        'data_format',
        'installation_date',
        'configuration',
        'communication_mode',
        'status',
        'updated_at',
        'last_active'
    ]
    list_display_links = ['name', 'operator']
    

admin.site.register(Sensor, SensorAdmin)



class SensorDataAdmin(admin.ModelAdmin):
    list_display = [
        'sensor',
        'data',
        'data_type',
        'latitude',
        'longitude',
        'unit_of_measurement',
        'date_added'
    ]
    list_display_links = ['sensor']
    

admin.site.register(SensorData, SensorDataAdmin)
    