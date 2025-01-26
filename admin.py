# admin.py
from django.contrib import admin
from .models import Customer, Compliance, Template, Employee, Policy, Acknowledgement, PolicyConfiguration, History

class CustomerAdmin(admin.ModelAdmin):
    search_fields = ('name',)
    list_display = ('id', 'name', 'is_deleted')
    
class ComplianceAdmin(admin.ModelAdmin):
    search_fields = ('compliance_title',)
    list_display = ('id', 'compliance_title', 'is_deleted')
    
class TemplateAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'description', 'created_at', 'updated_at')
    search_fields = ('name',)

# class TemplateVersionAdmin(admin.ModelAdmin):
#     list_display = ('id', 'template', 'version_number', 'is_latest', 'change_log', 'created_at')
    
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'email', 'customer', 'role', 'status', 'created_at', 'updated_at')
    search_fields = ('name', 'role',)
    
class PolicyAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'version', 'approval_status', 'approved_by',  'created_at', 'updated_at')
    search_fields = ('title', 'description',)
    
class PolicyConfigurationAdmin(admin.ModelAdmin):
    list_display = ('id', 'policy', 'key', 'version', 'status', 'created_at', 'updated_at')
    search_fields = ('title', 'description',)
    
# class CustomerPolicyAdmin(admin.ModelAdmin):
#     list_display = ('id', 'policy', 'version', 'status', 'created_at', 'updated_at')
#     search_fields = ('policy',)
    
class AcknowledgementAdmin(admin.ModelAdmin):
    list_display = ('id', 'policy', 'employee', 'status', 'acknowledgement_type', 'created_at', 'updated_at')
    search_fields = ('policy', 'employee',)
    
class HistoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'acknowledgement', 'field', 'updated_at')
    search_fields = ('field', 'status',)


admin.site.register(Employee, EmployeeAdmin)
admin.site.register(Customer, CustomerAdmin)
admin.site.register(Compliance, ComplianceAdmin)
admin.site.register(Template, TemplateAdmin)
# admin.site.register(TemplateVersion, TemplateVersionAdmin)
admin.site.register(Policy, PolicyAdmin)
admin.site.register(PolicyConfiguration, PolicyConfigurationAdmin)
# admin.site.register(CustomerPolicy, CustomerPolicyAdmin)
admin.site.register(Acknowledgement, AcknowledgementAdmin)
admin.site.register(History, HistoryAdmin)