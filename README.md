# Yatube

## Description
Social network for keeping personal records divided into groups. All authenticated users can comment and subscribe to other authors.  

## Running project
Yatube is template-type project. So you can download it and configure as you want.

Make sure that you have `python3.8^`, `python3-pip` and `python3-venv` on your local machine.

Then clone this repository machine and go to just reated project folder.

1. Create virtual environment and activate it:
```
python -m venv venv && source venv/bin/activate
```

2. Install the project dependencies:
```
pip install -r requirements.txt
```

3. Synchronize the database state with the current set of models and migrations: 
```
python manage.py migrate
```

4. Now you can up the project:
```
python manage.py runserver
```

## System requirements

* Ubuntu 16.^
* macOS High Sierra 10.13.6

## Stack

* [Python 3.8](https://www.python.org/)
* [Django](https://www.djangoproject.com/)
* [Pillow 8](https://pillow.readthedocs.io/)


## Author

Evan Vilagov

Linkedin: https://www.linkedin.com/in/vilagov/

Email: evan.vilagov@gmail.com
