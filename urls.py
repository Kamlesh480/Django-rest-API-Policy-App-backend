from policy.views import hello_world
from policy.views import get_customers, get_compliance, manage_templates, employee_view, policy_view, acknowledgement_view, customer_compliance_view, manage_policy_configurations
from django.urls import path

urlpatterns = [
    
    # Backend APIs for database interaction
    path('customers/', get_customers),
    path('compliances/', get_compliance),
    path('templates/', manage_templates, name='manage_templates'),
    # path('template-versions/', manage_template_versions, name='manage_template_versions'),
    path('employees/', employee_view, name='employee_view'),
    path('policies/', policy_view, name='policy-list-create'),
    # path('customer_policies/', customer_policy_view, name='customer_policy_view'),
    path('acknowledgements/', acknowledgement_view, name='acknowledgement_list_create'),
    path('customer-compliance/', customer_compliance_view, name='customer_compliance_view'),
    path('manage-policy-configurations/', manage_policy_configurations, name='manage_policy_configurations'),
    
    
    # Backend APIs for business logic operations
    
]
