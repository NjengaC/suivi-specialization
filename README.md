# SUIVI SPECIALISATION PROJECT

Welcome to SUIVI Parcel Sending Service App. This application provides a convenient platform for users to send parcels from one location to another. It is also a platform that offers secure and consistent work to the workforce.

## Features

### Homepage
The homepage serves as the first impression of the app, providing an overview of the services offered. Users can navigate to other sections of the app from here.

### User Registration/Login
Users can create accounts or log in with existing ones to access the features of the app.

### Parcel Sending Request Form
Users can fill out a form specifying the details of the parcel they want to send, including size, weight, pickup location, and destination.

### Riders and Parcel Service Companies Registration/Login
Riders and Parcel service companies can register accounts or log in to access their dashboard.

### Riders Dashboard
Riders can have access to a dashboard where they can manage parcel pickup requests, accept or reject assignments, update parcel statuses, and communicate with users.

### Parcel Tracking
Users can track the status of their parcels in real-time, from pickup to delivery.

### Payment Integration
Integration with a payment gateway facilitates transactions for parcel sending services.

### Rating and Feedback System
Users can rate and provide feedback on the parcel service companies they've used, helping other users make informed decisions.

### Mobile App Version
An Android app version of the web app will be available for users to conveniently access parcel sending services on their smartphones.

### Admin Panel
An admin panel allows for the management of user accounts, company registrations, monitoring of activity, and addressing any issues that arise.

## Running the App

To run the app in development mode, follow these steps:

1. Ensure you have Python 3 installed on your system.
2. Install the required dependencies by running:
    ```bash
    pip install -r requirements.txt
    ```
    or
   ```bash
    sudo ./flask_installs
    ```


4. Login into postgresql and create the database
  ```bash
  sudo -u postgres psql
  ```
```bash
CREATE DATABASE suivi
```
5. Navigate to the project's root directory and run the following commands to instantiate database.
   ```bash
   export FLASK_APP=run.py
   flask db init
   flask db migrate -m "Initial migration."
   flask db upgrade
   ```
   
6. Run the following command while at the root of the project directory:
   
    ```bash
    python3 run.py
    ```
7. Access the app in your web browser at http://127.0.0.1:5003

## Legal and Regulatory Considerations

No legal and regulatory considerations until deployment!
