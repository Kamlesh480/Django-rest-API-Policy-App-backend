from datetime import timedelta
from django.utils import timezone

from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ValidationError
from django.http import JsonResponse

from .models import Customer, Compliance, Template, Employee, Policy, Acknowledgement, CustomerCompliance, PolicyConfiguration
from .serializers import CommonSerializer


@api_view(['GET', 'POST'])
def hello_world(request):
    if request.method == 'POST':
        return Response({"message": "Got some data!", "data": request.data})
    return Response({"message": "Hello, world!"})


@api_view(['GET', 'POST'])
def get_customers(request):
    if request.method == 'GET':
        # Fetch all customers that are not deleted
        customers = Customer.objects.filter(is_deleted=False)
        
        # Dynamically set the model for the serializer
        serializer = CommonSerializer(instance=customers, many=True, model=Customer)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        customer_id = request.data.get('id')
        
        if customer_id:
            try:
                # Fetch the existing customer by ID
                customer = Customer.objects.get(id=customer_id, is_deleted=False)
                
                # Update the customer details using the provided data
                serializer = CommonSerializer(instance=customer, data=request.data, model=Customer, partial=True)
                
                if serializer.is_valid():
                    serializer.save()  # Save updated customer details
                    return Response(serializer.data, status=status.HTTP_200_OK)
                
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            except Customer.DoesNotExist:
                return Response({"error": "Customer not found."}, status=status.HTTP_404_NOT_FOUND)
        
        else:
            # Validate if a customer with the same name already exists
            customer_name = request.data.get('name')
            if Customer.objects.filter(name=customer_name, is_deleted=False).exists():
                return Response({"error": "A customer with this name already exists."}, status=status.HTTP_400_BAD_REQUEST)
            
            # If no existing customer, create a new customer
            serializer = CommonSerializer(data=request.data, model=Customer)
            
            if serializer.is_valid():
                new_customer = serializer.save()  # Save the new customer
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        

@api_view(['GET', 'POST'])
def get_compliance(request):
    if request.method == 'GET':
        # Fetch all non-deleted compliance records
        compliances = Compliance.objects.filter(is_deleted=False)
        
        # Use CommonSerializer dynamically with the Compliance model
        serializer = CommonSerializer(compliances, many=True, model=Compliance)
        
        # Return the response
        return Response(serializer.data)
    
    elif request.method == 'POST':
        data = request.data
        compliance_id = data.get('id')
        
        if compliance_id:
            try:
                # Fetch existing compliance for update
                compliance = Compliance.objects.get(id=compliance_id, is_deleted=False)
                
                # Update fields dynamically
                serializer = CommonSerializer(instance=compliance, data=data, model=Compliance, partial=True)
                
                if serializer.is_valid():
                    serializer.save()
                    return Response({"message": "Compliance updated successfully"}, status=status.HTTP_200_OK)
                
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            except Compliance.DoesNotExist:
                return Response({"error": "Compliance not found or has been deleted."}, status=status.HTTP_404_NOT_FOUND)
        
        # If no ID is provided, create a new compliance
        compliance_title = data.get('compliance_title')
        
        # Ensure the compliance title is unique
        if Compliance.objects.filter(compliance_title=compliance_title, is_deleted=False).exists():
            return Response({"error": "Compliance with this title already exists."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Create a new compliance
        serializer = CommonSerializer(data=data, model=Compliance)
        if serializer.is_valid():
            compliance = serializer.save()
            return Response({"message": "Compliance created successfully", "id": compliance.id}, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

@api_view(['GET', 'POST'])
def manage_templates(request):
    if request.method == 'GET':
        # Fetch all active templates
        templates = Template.objects.filter(is_active=True)
        serializer = CommonSerializer(templates, model=Template, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        template_id = request.data.get('id')
        is_latest = request.data.get('is_latest', False)  # Whether to mark as the latest version
        version_number = request.data.get('version_number')  # Version number for the template

        if template_id:
            # Updating an existing template
            try:
                template = Template.objects.get(id=template_id, is_active=True)
                serializer = CommonSerializer(template, data=request.data, partial=True, model=Template)

                if serializer.is_valid():
                    serializer.save()

                    # Handle `is_latest` logic
                    if is_latest:
                        template.is_latest = True
                        template.save()

                    return Response(serializer.data, status=status.HTTP_200_OK)
                else:
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            except Template.DoesNotExist:
                return Response({"error": "Template not found or is inactive."}, status=status.HTTP_404_NOT_FOUND)
        else:
            # Creating a new template (assumes a new version of an existing template or a brand-new template)
            serializer = CommonSerializer(data=request.data, model=Template)

            if serializer.is_valid():
                new_template = serializer.save()

                # Handle `is_latest` and ensure only one is marked latest
                if is_latest:
                    Template.objects.filter(name=new_template.name).update(is_latest=False)
                    new_template.is_latest = True
                    new_template.save()

                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# @api_view(['GET', 'POST'])
# def manage_template_versions(request):
#     if request.method == 'GET':
#         # Fetch all template versions
#         template_versions = TemplateVersion.objects.all()
#         serializer = CommonSerializer(instance=template_versions, many=True, model=TemplateVersion)
#         return Response(serializer.data)

#     elif request.method == 'POST':
#         # Handle creation and updates
#         version_id = request.data.get('id')

#         if version_id:
#             try:
#                 version = TemplateVersion.objects.get(id=version_id)
#                 serializer = CommonSerializer(instance=version, data=request.data, model=TemplateVersion, partial=True)
#                 if serializer.is_valid():
#                     serializer.save()
#                     return Response(serializer.data, status=status.HTTP_200_OK)
#                 return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#             except TemplateVersion.DoesNotExist:
#                 return Response({"error": "Template version not found."}, status=status.HTTP_404_NOT_FOUND)

#         # Create a new template version
#         template_id = request.data.get('template')
#         try:
#             template = Template.objects.get(id=template_id)
#         except Template.DoesNotExist:
#             return Response({"error": "Template not found."}, status=status.HTTP_404_NOT_FOUND)

#         # Calculate the next version number
#         latest_version = TemplateVersion.objects.filter(template=template).order_by('-version_number').first()
#         new_version_number = latest_version.version_number + 1 if latest_version else 1

#         # Ensure only one version is marked as latest
#         data = request.data.copy()
#         data['template'] = template.id
#         data['version_number'] = new_version_number

#         serializer = CommonSerializer(data=data, model=TemplateVersion)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

@api_view(['GET', 'POST'])
def employee_view(request):
    if request.method == 'GET':
        # Fetch all non-deleted employees for customers that are not deleted
        employees = Employee.objects.filter(customer__is_deleted=False)
        serializer = CommonSerializer(employees, model=Employee, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        employee_id = request.data.get('id')

        if employee_id:
            # Updating an existing employee
            try:
                employee = Employee.objects.get(id=employee_id, customer__is_deleted=False)
                serializer = CommonSerializer(employee, data=request.data, partial=True, model=Employee)

                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data, status=status.HTTP_200_OK)
                else:
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            except Employee.DoesNotExist:
                return Response({"error": "Employee not found or associated customer is deleted."}, status=status.HTTP_404_NOT_FOUND)
        else:
            # Creating a new employee
            customer_id = request.data.get('customer')
            customer = get_object_or_404(Customer, id=customer_id, is_deleted=False)

            serializer = CommonSerializer(data=request.data, model=Employee)

            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'POST', 'PUT'])
def policy_view(request):
    if request.method == 'GET':
        # Fetch all policies with active status
        policies = Policy.objects.filter(is_deleted=False)  # Assuming 'is_deleted' is a boolean field
        serializer = CommonSerializer(policies, model=Policy, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        # Creating a new policy
        policy_type = request.data.get('type')
        if policy_type not in ['default', 'custom']:
            return Response({"error": "Invalid policy type."}, status=status.HTTP_400_BAD_REQUEST)

        if policy_type == 'default':
            # Default policy logic: must have a template
            template_id = request.data.get('template')
            if not template_id:
                return Response({"error": "Template is required for default policies."}, status=status.HTTP_400_BAD_REQUEST)

            try:
                template = Template.objects.get(id=template_id, is_latest=True)
            except Template.DoesNotExist:
                return Response({"error": "Template not found or is not the latest version."}, status=status.HTTP_404_NOT_FOUND)

            # Create the default policy
            request.data['version'] = template.version_number  # Set version from template
            request.data['approval_status'] = 'pending'  # Default is 'pending' approval status
            serializer = CommonSerializer(data=request.data, model=Policy)

            if serializer.is_valid():
                # Create the policy, setting the template
                serializer.save(template=template)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        elif policy_type == 'custom':
            # Custom policy logic: must specify created_by and document link
            created_by_id = request.data.get('created_by')
            document_link = request.data.get('document_link')

            if not created_by_id or not document_link:
                return Response({"error": "Created by and document link are required for custom policies."},
                                 status=status.HTTP_400_BAD_REQUEST)

            try:
                created_by = Employee.objects.get(id=created_by_id)
            except Employee.DoesNotExist:
                return Response({"error": "Employee not found."}, status=status.HTTP_404_NOT_FOUND)

            # Create the custom policy
            request.data['approval_status'] = 'pending'  # Default is 'pending' approval status
            serializer = CommonSerializer(data=request.data, model=Policy)

            if serializer.is_valid():
                serializer.save(created_by=created_by)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'PUT':
        # Update an existing policy (e.g., approve/reject policy)
        policy_id = request.data.get('id')
        if not policy_id:
            return Response({"error": "Policy ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            policy = Policy.objects.get(id=policy_id)
        except Policy.DoesNotExist:
            return Response({"error": "Policy not found."}, status=status.HTTP_404_NOT_FOUND)

        # Update the approval status or other details
        approval_status = request.data.get('approval_status')
        if approval_status:
            if approval_status not in ['pending', 'approved', 'rejected']:
                return Response({"error": "Invalid approval status."}, status=status.HTTP_400_BAD_REQUEST)
            policy.approval_status = approval_status
            if approval_status == 'approved':
                policy.approved_at = timezone.now()  # Set the approval timestamp
            elif approval_status == 'rejected':
                policy.approved_at = None  # Reset the approval timestamp if rejected

        serializer = CommonSerializer(policy, data=request.data, partial=True, model=Policy)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'POST'])
def manage_policy_configurations(request):
    if request.method == 'GET':
        # Fetch all policy configurations
        policy_configurations = PolicyConfiguration.objects.all()
        serializer = CommonSerializer(policy_configurations, model=PolicyConfiguration, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        # Check for ID in the request data to update or create
        config_id = request.data.get('id')  # Check if there's an ID to update an existing config

        if config_id:
            try:
                # Updating an existing configuration
                policy_config = PolicyConfiguration.objects.get(id=config_id)
                serializer = CommonSerializer(policy_config, data=request.data, partial=True, model=PolicyConfiguration)

                if serializer.is_valid():
                    serializer.save()  # Save the updated configuration
                    return Response(serializer.data, status=status.HTTP_200_OK)
                else:
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            except PolicyConfiguration.DoesNotExist:
                return Response({"error": "Configuration not found."}, status=status.HTTP_404_NOT_FOUND)
        else:
            # Creating a new configuration
            policy_id = request.data.get('policy')
            key = request.data.get('key')
            value = request.data.get('value')

            # Ensure that the policy exists
            try:
                policy = Policy.objects.get(id=policy_id)
            except Policy.DoesNotExist:
                return Response({"error": "Policy not found."}, status=status.HTTP_404_NOT_FOUND)

            # Creating the policy configuration
            serializer = CommonSerializer(data=request.data, model=PolicyConfiguration)

            if serializer.is_valid():
                # Save the configuration and trigger versioning
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# @api_view(['GET', 'POST'])
# def customer_policy_view(request):
#     if request.method == 'GET':
#         # Fetch all active customer policies
#         policies = CustomerPolicy.objects.all()
#         serializer = CommonSerializer(policies, model=CustomerPolicy, many=True)
#         return Response(serializer.data)

#     elif request.method == 'POST':
#         policy_id = request.data.get('id')

#         if policy_id:
#             # Update an existing CustomerPolicy
#             try:
#                 customer_policy = CustomerPolicy.objects.get(id=policy_id)
#                 serializer = CommonSerializer(customer_policy, data=request.data, partial=True, model=CustomerPolicy)

#                 if serializer.is_valid():
#                     serializer.save()
#                     return Response(serializer.data, status=status.HTTP_200_OK)
#                 else:
#                     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#             except CustomerPolicy.DoesNotExist:
#                 return Response({"error": "Customer Policy not found."}, status=status.HTTP_404_NOT_FOUND)
#         else:
#             # Create a new CustomerPolicy (if no id is provided)
#             customer_compliance_id = request.data.get('customer_compliance')
#             policy_id = request.data.get('policy')
#             approval_requested_by_id = request.data.get('approval_requested_by')

#             # Ensure the customer_compliance, policy, and approval_requested_by exist
#             try:
#                 customer_compliance = CustomerCompliance.objects.get(id=customer_compliance_id)
#                 policy = Policy.objects.get(id=policy_id)
#                 approval_requested_by = Employee.objects.get(id=approval_requested_by_id)
#             except (CustomerCompliance.DoesNotExist, Policy.DoesNotExist, Employee.DoesNotExist) as e:
#                 return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

#             # Create new CustomerPolicy entry
#             serializer = CommonSerializer(data=request.data, model=CustomerPolicy)
#             if serializer.is_valid():
#                 serializer.save()
#                 return Response(serializer.data, status=status.HTTP_201_CREATED)
#             else:
#                 return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'POST'])
def acknowledgement_view(request, pk=None):
    if request.method == 'GET':
        # Retrieve all acknowledgements
        acknowledgements = Acknowledgement.objects.all()
        serializer = CommonSerializer(acknowledgements, many=True, model=Acknowledgement)
        return Response({
            "message": "Acknowledgements retrieved successfully",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        # If an 'id' is present in the request data, it's for updating an existing record
        if 'id' in request.data:
            try:
                # Retrieve the existing Acknowledgement
                acknowledgement = Acknowledgement.objects.get(id=request.data['id'])
            except Acknowledgement.DoesNotExist:
                return Response({
                    "error": "Acknowledgement not found."
                }, status=status.HTTP_404_NOT_FOUND)

            # Use the serializer to update the existing record
            serializer = CommonSerializer(acknowledgement, data=request.data, partial=True, model=Acknowledgement)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    "message": "Acknowledgement updated successfully",
                    "data": serializer.data
                }, status=status.HTTP_200_OK)
            return Response({
                "error": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        else:
            # Creating a new Acknowledgement
            acknowledgement_data = request.data

            # Validate acknowledgment for 'new_joiner' type
            if acknowledgement_data.get('acknowledgement_type') == 'new_joiner':
                try:
                    # Retrieve the employee
                    employee = Employee.objects.get(id=acknowledgement_data['employee'])
                    
                    # Check if the employee joined within 30 days
                    join_date = employee.created_at
                    if join_date + timedelta(days=30) < timezone.now():
                        raise ValidationError("Acknowledgement for new joiner must be completed within 30 days of joining.")
                except Employee.DoesNotExist:
                    return Response({
                        "error": "Employee not found."
                    }, status=status.HTTP_404_NOT_FOUND)
                except ValidationError as e:
                    return Response({
                        "error": str(e)
                    }, status=status.HTTP_400_BAD_REQUEST)

            # Now, create the acknowledgement
            serializer = CommonSerializer(data=acknowledgement_data, model=Acknowledgement)
            if serializer.is_valid():
                # Create new acknowledgement entry
                serializer.save()
                return Response({
                    "message": "Acknowledgement created successfully",
                    "data": serializer.data
                }, status=status.HTTP_201_CREATED)
            return Response({
                "error": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
            
            
# API view function for handling CustomerCompliance
@api_view(['GET', 'POST'])
def customer_compliance_view(request):
    if request.method == 'GET':
        # Fetch all active customer compliances
        customer_compliances = CustomerCompliance.objects.all()
        serializer = CommonSerializer(customer_compliances, model=CustomerCompliance, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        customer_compliance_id = request.data.get('id') or request.query_params.get('id')  # Get id from body or query param

        if customer_compliance_id:
            # Updating an existing customer compliance
            try:
                customer_compliance = CustomerCompliance.objects.get(id=customer_compliance_id)
                serializer = CommonSerializer(customer_compliance, data=request.data, partial=True, model=CustomerCompliance)

                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data, status=status.HTTP_200_OK)
                else:
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            except CustomerCompliance.DoesNotExist:
                return Response({"error": "Customer compliance not found."}, status=status.HTTP_404_NOT_FOUND)
        else:
            # Creating a new customer compliance
            serializer = CommonSerializer(data=request.data, model=CustomerCompliance)

            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)