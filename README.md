# Django-rest-API-Policy-App-backend

## Project Overview
This project is a comprehensive system designed to manage customer data, compliance, policies, employee information, acknowledgements, and notifications. The architecture is built around a microservices-based approach, where various services communicate with each other to handle specific functionalities. The system leverages a robust database model that ensures efficient management of entities across multiple services. <br><br>

## Key Components:
Client Side: The frontend interface for users to interact with the system, providing access to features like policy creation, employee management, and acknowledgement tracking.<br>
API Gateway: The entry point for all requests, responsible for routing, authentication, and load balancing.<br>
Customer Service: Manages customer-related data, including customer profiles and subscriptions.<br>
Employee Service: Handles employee data and assigns relevant policies based on roles.<br>
Compliance Service: Manages compliance requirements for customers and tracks policy adherence.<br>
Policy Service: Manages the creation, modification, and configuration of policies. Handles policy versioning and approval processes.<br>
Acknowledgement Service: Tracks employee acknowledgements of policies, ensuring they are completed within the required timeframe.<br>
Notification Service: Sends notifications for policy updates, acknowledgement reminders, and escalation alerts.<br>
Database Models:<br>
The system uses a set of well-defined database models to store and manage critical data. These include:<br>

Customer Model: Stores customer-specific information such as name, subscription type, and employee associations.<br>
Employee Model: Manages employee data including roles, status, and associations with specific policies.<br>
Compliance Model: Tracks compliance requirements, statuses, and related audits.<br>
Policy Model: Stores policy details, versioning, and associations with templates and customers.<br>
Policy Configuration Model: Manages configuration settings for policies, including version control and status.<br>
Acknowledgement Model: Tracks the status of employee acknowledgements for policies, ensuring timely responses.<br>
Customer Compliance Model: Links customers with compliance requirements and tracks their progress.<br>
These models enable efficient management of data and provide the foundation for various services like policy approval, employee onboarding, compliance tracking, and acknowledgement monitoring.<br>

## System Flow:
The client interacts with the API Gateway, which routes requests to the appropriate backend services. Services like Customer, Employee, Policy, and Acknowledgement work together to manage policies, track compliance, and ensure employees acknowledge policies within the required timeframes. The Notification Service sends alerts when actions are required or due.<br>
The database models serve as the backbone for all data storage, ensuring that data integrity is maintained and that all services have access to the information they need to function properly.<br>
This project ensures efficient management of customer policies, compliance tracking, and employee engagement, with robust authentication, approval processes, and notification handling, all powered by a structured and scalable database design.<br>



## Commands:
python3.8 -m venv env
source env/bin/activate

python3 manage.py runserver

python3 manage.py makemigrations
python3 manage.py migrate

python3 manage.py createsuperuser

// genrate image ERD:
python manage.py graph_models -a -g -o myapp_erd.png
