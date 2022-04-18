# University of Essex - MSc CyberSecurity - Secure Software Development Module - March 2022

## Introduction ##

An application was developed for securely exchanging data between the ISS (International Space Station) and the ground centre staff. The application is written in Python 3.10.3 and provides the following functionalities:

* User Registration and Login
* File Search & Download
* File Upload
* File Share

### Pre-Requisites

The following pre-requisites are required to successfully run the code:

* Python 3.10.3
* MySQL Database - a script called ***issdes.sql*** is provided to create the database schema using Querious (Araelium Group, 2021). 
 
The following python libraries are required:

* Flask 2.1.1
* Flask-Login 0.60
* Flask-SQLAlchemy 2.5.1
* mysql-connector-python 8.0.28
* Werkzeug 2.1.1
* MarkupSafe 2.1.1
* Python-dotenv 0.20.0
* gunicorn 20.1.0

## Code Structure ##

The code structure is as follows:

![This is an image](https://github.com/ssdgroup2/issdes/blob/main/images/codestructure.png)

`app.py` - This is the main application used to route searching, sharing, uploading and downloading requests to the appropriate URL's. Front end forms are displayed using html templates obtained from Bulma (2022).

`authentication.py` - This code is required for authenticating end users as well as performing input validations. When a user's password is entered during the registration process it is encrypted using the werkzeug.security module and stored in a MySQL database with the corresponding user id. Screenshot below:

![This is an image](https://github.com/ssdgroup2/issdes/blob/main/images/dbs1.png)

In addition, Flask libraries and modules are used to handle user session management. (Flask, N.D.).

`__init__.py` - Used to initialise the main structure of the application making use of Flask libraries (Pallets, 2010).

`config.py` - Used to store secret key for MySQL DB.

`db.py` - Used to connect to the MySQL DB.

`dbmodel.py` - Used to create DB structure based on Python classes (Stackoverflow, 2019).

`repetitives.py` - Numerous data processing stages need to be repeated within different parts of the application. Therefore, instead of coding repeating functions this module can be reused. It does allow easy reuse of these custom functions in `app.py` and `authentication.py`.

`appsecmon.py` - Used to generate logging information (Python Software Foundation, 2022).

## User Registration ##

Files named ***usermanagementutil.py*** and ***makeissdesuser.py*** are used to register users to the system. It is assumed that the CLI will be used to perform user registration. The code is executed as follows: `python3 makeissdesuser.py` and produces the following output:

![This is an image](https://github.com/ssdgroup2/issdes/blob/main/images/userreg.png)

Users are created and placed into AuthGroups allowing only users within an AuthGroup to share files with each other. In the case where a user's profile has been hacked, the attacker would not gain access to files uploaded from other users, minimising the attack surface. The following Authorisation Groups are used:

Auth Group    | Country
------------- | -------------
14            | Europe
11            | USA
19            | Canada
15            | Japan
12            | Russia

Once completed the user will be required to save their AccessID and Password. These credentials will be used to login to the application.

## Main Application ##

The main application is executed by running: `flask run` and produces the following output:

![This is an image](https://github.com/ssdgroup2/issdes/blob/main/images/flaskoutput.png)

Once successful, the application will be accessible from the web browser on: `http://127.0.0.1:8080`

![This is an image](https://github.com/ssdgroup2/issdes/blob/main/images/issdesui.png)

## Discussion - Design & Coding Differences ##

During the design phase the following requirements were established:

* Perform CRUD (Create, Read, Update and Delete) operations
* Perform moderate-level input validations
* Exchange data between groups
* Revoke user accounts (Inactivity = 90 days)
* Database Replication

The final code achieved the CRUD operation requirements, input validations and was also able to share files between groups. However the code did not meet the objectives of revocation of user accounts as well as database replication due to time constraints (21 days). These items should be included as future work.

The difference in selected libraries during the design and coding phase are listed below:

![This is an image](https://github.com/ssdgroup2/issdes/blob/main/images/diff_library.png)

## Functional Testing Images ##

Nova was used as a code editor with built in extensions for Python, Pylint and Flake8 - this allowed automatic testing and correction:

![This is an image](https://github.com/ssdgroup2/issdes/blob/main/images/nova.png)

User Login Screen:

![This is an image](https://github.com/ssdgroup2/issdes/blob/main/images/userlogin.png)

File Upload Success Screen:

![This is an image](https://github.com/ssdgroup2/issdes/blob/main/images/Fileupload.png)

File stored in DB:

![This is an image](https://github.com/ssdgroup2/issdes/blob/main/images/filestored.png)

Search for a File:

![This is an image](https://github.com/ssdgroup2/issdes/blob/main/images/search1.png)

![This is an image](https://github.com/ssdgroup2/issdes/blob/main/images/search2.png)

## References ##

Araelium Group (2021) Araelium. Available from: https://www.araelium.com/support/querious/download-previous-versions [Accessed 30 March 2022].

Bulma (2022) Bulma: the modern CSS framework that just works. Available from: https://bulma.io/ [Accessed 29 March 2022].

Flask (N.D.) Flask-Login. Available from: https://flask-login.readthedocs.io/en/latest/ [Accessed 30 March 2022].

Pallets (2010) The Application Context. Available from: https://flask.palletsprojects.com/en/2.1.x/appcontext/ [Accessed 02 April 2022].

Python Software Foundation (2022) Unix syslog library routines. Available from: https://docs.python.org/3/library/syslog.html [Accessed 09 April 2022].

Stackoverflow (2019) Django: Does "primary_key=True" also mean "unique"? Available from: https://stackoverflow.com/questions/58139212/django-does-primary-key-true-also-mean-unique [Accessed 07 April 2022].


