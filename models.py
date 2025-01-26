from django.db import models
from datetime import timedelta
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.core.mail import send_mail

class Customer(models.Model):
    SUBSCRIPTION_CHOICES = [
        ('free', 'Standard'),
        ('standard', 'free'),
        ('premium', 'Premium'),
    ]
    
    # Basic fields
    name = models.CharField(max_length=255)
    subscription_type = models.CharField(
        max_length=10,
        choices=SUBSCRIPTION_CHOICES,
        default='free'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    
    # Soft delete flag
    is_deleted = models.BooleanField(default=False)
    
    def delete(self, using=None, keep_parents=False):
        """Soft delete - marks the entry as deleted instead of removing it from the database."""
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save()

    def __str__(self):
        return self.name


class Compliance(models.Model):
    COMPLIANCE_CHOICES = [
        ('infosec', 'Infosec Policy'),
        ('acceptable_use', 'Acceptable Use Policy'),
        ('cryptographic', 'Cryptographic Policy'),
        # Add more compliance types as needed
    ]

    # Basic fields
    compliance_type = models.CharField(
        max_length=50,
        choices=COMPLIANCE_CHOICES,
        default='infosec'
    )

    compliance_title = models.CharField(max_length=255)
    is_deleted = models.BooleanField(default=False)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    # Soft delete functionality
    def delete(self, using=None, keep_parents=False):
        """Soft delete - marks the entry as deleted instead of removing it from the database."""
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save()

    def __str__(self):
        return f"{self.compliance_title} ({self.compliance_type})"


class Template(models.Model):
    name = models.CharField(max_length=255)  # Template name
    description = models.TextField(blank=True, null=True)  # Template description
    document_link = models.URLField(blank=True, null=True)  # URL to the document file
    version_number = models.PositiveIntegerField(default=1)  # Explicit version number
    is_latest = models.BooleanField(default=False)  # Indicates if this is the latest version
    is_active = models.BooleanField(default=True)  # Indicates if the template is active
    change_log = models.TextField(blank=True, null=True)  # Description of changes in this version
    created_at = models.DateTimeField(auto_now_add=True)  # Auto-created timestamp
    updated_at = models.DateTimeField(auto_now=True)  # Auto-updated timestamp

    def save(self, *args, **kwargs):
        """
        Ensure only one version of the same template (by name) is marked as the latest.
        """
        if self.is_latest:
            # Set `is_latest=False` for all other versions of the same template name
            Template.objects.filter(name=self.name).update(is_latest=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} - Version {self.version_number}"


# class TemplateVersion(models.Model):
#     template = models.ForeignKey(
#         Template, on_delete=models.CASCADE, related_name="versions"
#     )  # Links to the Template table
#     document_link = models.URLField()  # URL to the document file
#     version_number = models.PositiveIntegerField()  # Explicit version number
#     is_latest = models.BooleanField(default=False)  # Indicates whether this is the latest version
#     change_log = models.TextField(blank=True, null=True)  # Description of changes in this version
#     created_at = models.DateTimeField(auto_now_add=True)  # Auto-generated created timestamp

#     def save(self, *args, **kwargs):
#         """
#         When marking a version as the latest, ensure no other version
#         of the same template is marked as latest.
#         """
#         if self.is_latest:
#             TemplateVersion.objects.filter(template=self.template).update(
#                 is_latest=False
#             )
#         super().save(*args, **kwargs)

#     def __str__(self):
#         return f"{self.template.name} - Version {self.version_number}"



class Employee(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    ]

    name = models.CharField(max_length=255)  # Employee name
    email = models.EmailField(unique=True)  # Employee email
    customer = models.ForeignKey(
        'Customer', on_delete=models.CASCADE, related_name='employees'
    )  # Link to the customer's company
    role = models.CharField(max_length=255)  # Employee's role
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default='active'
    )  # Active/inactive employee
    join_date = models.DateTimeField(null=True, blank=True)  # Employee join date (new field)
    created_at = models.DateTimeField(auto_now_add=True)  # Auto-created timestamp
    updated_at = models.DateTimeField(auto_now=True)  # Auto-updated timestamp

    def __str__(self):
        return self.name


class Policy(models.Model):
    POLICY_TYPE_CHOICES = [
        ('default', 'Default'),  # Based on a template
        ('custom', 'Custom'),    # Created directly by a customer
    ]

    APPROVAL_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    type = models.CharField(
        max_length=10, choices=POLICY_TYPE_CHOICES, default='default'
    )  # Policy type
    title = models.CharField(max_length=255)  # Policy title
    description = models.TextField(blank=True, null=True)  # Policy description
    customer_compliance = models.ForeignKey(
        'CustomerCompliance', on_delete=models.SET_NULL, null=True, blank=True, related_name='policies'
    )  # Link to CustomerCompliance (for customer-specific policies)
    template = models.ForeignKey(
        Template, on_delete=models.SET_NULL, null=True, blank=True, related_name='policies'
    )  # Reference to a template (only for default policies)
    created_by = models.ForeignKey(
        'Employee', on_delete=models.SET_NULL, null=True, blank=True, related_name='custom_policies'
    )  # Employee who created the custom policy
    version = models.PositiveIntegerField(default=1)  # Version of the policy
    document_link = models.URLField(blank=True, null=True)  # URL to the policy document (for custom policies)
    approval_status = models.CharField(
        max_length=20, choices=APPROVAL_STATUS_CHOICES, default='pending'
    )  # Approval status for the policy
    approved_by = models.ForeignKey(
        'Employee', on_delete=models.SET_NULL, null=True, blank=True, related_name='policy_approvals'
    )  # Employee who approved the policy
    approved_at = models.DateTimeField(null=True, blank=True)  # Approval timestamp
    approval_requested_at = models.DateTimeField(auto_now_add=True)  # Approval request timestamp
    created_at = models.DateTimeField(auto_now_add=True)  # Auto-created timestamp
    updated_at = models.DateTimeField(auto_now=True)  # Auto-updated timestamp
    is_deleted = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        """
        Automatically set the version for default policies using the associated template.
        Automatically updates approval status when a new policy is created or modified.
        """
        if self.type == 'default' and self.template:
            latest_template = Template.objects.filter(
                name=self.template.name, is_latest=True
            ).first()
            if latest_template:
                self.template = latest_template
                self.version = latest_template.version_number
        if self.approval_status == 'approved' and not self.approved_at:
            self.approved_at = timezone.now()  # Set approval timestamp if approved
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} (Type: {self.type}, Version: {self.version}, Status: {self.approval_status})"


class PolicyConfiguration(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending Approval'),
        ('active', 'Active'),
        ('rejected', 'Rejected'),
    ]

    policy = models.ForeignKey(Policy, on_delete=models.CASCADE)  # Links to the Policy table
    key = models.CharField(max_length=255)  # Configuration key (e.g., vulnerability_sla)
    value = models.CharField(max_length=255)  # Configuration value (e.g., 7 days)
    version = models.PositiveIntegerField(default=1)  # Version of the configuration
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')  # Status of the configuration
    created_at = models.DateTimeField(auto_now_add=True)  # Creation timestamp
    updated_at = models.DateTimeField(auto_now=True)  # Last updated timestamp

    def __str__(self):
        return f"Configuration for {self.policy.title} - {self.key}: {self.value} (Version: {self.version})"
    
    def save(self, *args, **kwargs):
        """
        Automatically set the version of the policy configuration and trigger a policy version increment.
        """
        if not self.version:
            self.version = self.policy.version + 1  # Increment policy version when a new config is added
            self.policy.version = self.version  # Update policy version to the new version
            self.policy.save()
        super().save(*args, **kwargs)


# class CustomerPolicy(models.Model):
#     APPROVAL_STATUS_CHOICES = [
#         ('pending', 'Pending'),
#         ('approved', 'Approved'),
#         ('rejected', 'Rejected'),
#     ]
    
#     customer_compliance = models.ForeignKey('CustomerCompliance', null=True, blank=True, on_delete=models.CASCADE)  # Link to CustomerCompliance
#     policy = models.ForeignKey(Policy, on_delete=models.CASCADE)  # Link to the policy
#     version = models.PositiveIntegerField(default=1)  # Track the version of the policy for this customer
#     approved_by = models.ForeignKey('Employee', on_delete=models.SET_NULL, null=True, blank=True, related_name='approvals')
#     approved_at = models.DateTimeField(null=True, blank=True)
#     approval_requested_by = models.ForeignKey('Employee', on_delete=models.SET_NULL, null=True, blank=True, related_name='approval_requests')
#     approval_requested_at = models.DateTimeField(auto_now_add=True)
#     approval_status = models.CharField(max_length=20, choices=APPROVAL_STATUS_CHOICES, default='pending')
#     approval_approved_at = models.DateTimeField(null=True, blank=True)
#     status = models.CharField(max_length=20, choices=[('active', 'Active'), ('inactive', 'Inactive'), ('pending', 'Pending')], default='pending')
#     created_at = models.DateTimeField(auto_now_add=True)  # When the record was created
#     updated_at = models.DateTimeField(auto_now=True)  # When the record was last updated

#     def __str__(self):
#         return f"Policy for Compliance {self.customer_compliance.id} - {self.policy.title} (Version {self.version})"
    
#     def save(self, *args, **kwargs):
#         """
#         When saving, ensure that the version is set to the current version of the policy if it's not already provided.
#         """
#         if not self.version:
#             self.version = self.policy.version  # Ensure version matches policy version
#         super().save(*args, **kwargs)


class Acknowledgement(models.Model):
    ACKNOWLEDGEMENT_TYPE_CHOICES = [
        ('new_joiner', 'New Joiner'),
        ('periodic', 'Periodic'),
        ('manual', 'Manual'),
        # Add more types if needed in the future
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('acknowledged', 'Acknowledged'),
    ]
    
    ESCALATION_STATUS_CHOICES = [
        ('none', 'None'),
        ('escalated_to_hr', 'Escalated to HR'),
        ('escalated_to_cxo', 'Escalated to CXO/CTO'),
    ]
    
    policy = models.ForeignKey(
        'Policy', on_delete=models.CASCADE, related_name='acknowledgements'
    )
    employee = models.ForeignKey(
        'Employee', on_delete=models.CASCADE, related_name='acknowledgements'
    )
    
    policy_version = models.PositiveIntegerField(default=1)
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    acknowledgement_type = models.CharField(
        max_length=15, choices=ACKNOWLEDGEMENT_TYPE_CHOICES
    )
    status = models.CharField(
        max_length=15, choices=STATUS_CHOICES, default='pending'
    )
    escalation_status = models.CharField(
        max_length=25, choices=ESCALATION_STATUS_CHOICES, default='none'
    )
    due_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.employee.name} - {self.policy.title} (Version {self.policy_version})"
    
    def save(self, *args, **kwargs):
        # Set due_date for new joiners, periodic, and manual acknowledgments
        if not self.pk:  # if this is a new instance
            if self.acknowledgement_type == 'new_joiner':
                self.due_date = self.employee.join_date + timedelta(days=30)
            elif self.acknowledgement_type == 'periodic':
                self.due_date = self.employee.join_date + timedelta(days=365)  # Example: 1 year after the previous acknowledgment
            elif self.acknowledgement_type == 'manual':
                self.due_date = timezone.now() + timedelta(days=30)
                
        # Validate no duplicate acknowledgments for the same policy version
        if not self.pk:  # if this is a new instance
            if Acknowledgement.objects.filter(employee=self.employee, policy=self.policy, policy_version=self.policy_version).exists():
                raise ValidationError(f"Acknowledgement for employee {self.employee.name} and policy {self.policy.policy.title} (Version {self.policy_version}) already exists.")
        
        # Check if acknowledgment is overdue and escalate
        if self.due_date and self.status == 'pending' and timezone.now() > self.due_date:
            self.escalate_acknowledgment()

        # Audit trail logic: Create a history record for critical field changes
        if self.pk:  # If it's an update, log the change
            self.create_audit_trail()

        super().save(*args, **kwargs)

    def escalate_acknowledgment(self):
        """Escalate acknowledgment to HR and then CXO/CTO based on overdue threshold."""
        overdue_days = (timezone.now() - self.due_date).days

        if self.escalation_status == 'none' and overdue_days >= 7:
            self.escalation_status = 'escalated_to_hr'
            self.save()
            # Send email to HR about the overdue acknowledgment
            self.send_escalation_email('HR')

        elif self.escalation_status == 'escalated_to_hr' and overdue_days >= 14:
            self.escalation_status = 'escalated_to_cxo'
            self.save()
            # Send email to CXO/CTO about the overdue acknowledgment
            self.send_escalation_email('CXO/CTO')

    def send_escalation_email(self, role):
        """Send email to notify stakeholders (HR or CXO/CTO) about escalation."""
        subject = f"Overdue Acknowledgment - Escalated to {role}"
        message = f"Dear {role},\n\nThe acknowledgment for the policy '{self.policy.policy.title}' by {self.employee.name} is overdue and has been escalated."
        recipient = ['hr@company.com'] if role == 'HR' else ['cxo@company.com', 'cto@company.com']

        send_mail(subject, message, 'no-reply@company.com', recipient)

    def send_acknowledgment_confirmation_email(self):
        """Send email to employee confirming successful acknowledgment."""
        subject = f"Policy Acknowledgment Confirmation"
        message = f"Dear {self.employee.name},\n\nYou have successfully acknowledged the policy '{self.policy.policy.title}' (Version {self.policy_version}). Thank you!"
        recipient = [self.employee.email]

        send_mail(subject, message, 'no-reply@company.com', recipient)

    def is_acknowledged_on_time(self):
        """Check if acknowledgment was completed within the due date."""
        if self.acknowledged_at and self.due_date:
            return self.acknowledged_at <= self.due_date
        return False

    def create_audit_trail(self):
        """Create an audit record when important fields are updated."""
        if self.status == 'acknowledged' and self.acknowledged_at and not self.history.exists():
            History.objects.create(
                acknowledgement=self,
                field='status',
                old_value='pending',
                new_value=self.status,
                updated_at=self.updated_at
            )
        elif self.status == 'pending' and self.acknowledged_at:
            History.objects.create(
                acknowledgement=self,
                field='acknowledged_at',
                old_value=None,
                new_value=self.acknowledged_at,
                updated_at=self.updated_at
            )


class History(models.Model):
    acknowledgement = models.ForeignKey(
        'Acknowledgement',
        on_delete=models.CASCADE,
        related_name='history'  # Ensure this matches self.history in your method
    )
    field = models.CharField(max_length=255)
    old_value = models.TextField(null=True, blank=True)
    new_value = models.TextField(null=True, blank=True)
    updated_at = models.DateTimeField()

    def __str__(self):
        return f"Audit for {self.acknowledgement} - {self.field}"

class CustomerCompliance(models.Model):
    customer = models.ForeignKey('Customer', on_delete=models.CASCADE)
    compliance = models.ForeignKey('Compliance', on_delete=models.CASCADE)
    
    # Compliance status (Pending, In Progress, Completed)
    status = models.CharField(
        max_length=20, choices=[('pending', 'Pending'), ('in_progress', 'In Progress'), ('completed', 'Completed')],
        default='pending'
    )
    
    # Percentage of completion for the compliance (from 0 to 100)
    compliance_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    
    # Date when the compliance audit was done
    audit_date = models.DateTimeField(null=True, blank=True)
    
    # Audit status (Pending, Completed)
    audit_status = models.CharField(
        max_length=20, choices=[('pending', 'Pending'), ('completed', 'Completed')],
        default='pending'
    )

    # Number of policies acknowledged
    acknowledged_count = models.PositiveIntegerField(default=0)
    
    # Number of policies pending acknowledgment
    pending_count = models.PositiveIntegerField(default=0)
    
    # Track if there are any changes made to the compliance
    compliance_updated = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)  # When the record was created
    updated_at = models.DateTimeField(auto_now=True)  # When the record was last updated

    def __str__(self):
        return f"Compliance for {self.customer.name} - {self.compliance.name} (Status: {self.status})"



