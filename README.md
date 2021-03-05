# hw05_final

Social network for keeping personal records divided into groups; with the ability to comment and subscribe to other authors.  

## Running this project
This project requires Python version 3.8.

Install the project dependencies with
```
pip install -r requirements.txt
```

Synchronize the database state with the current set of models and migrations. 
```
python manage.py migrate
```

Now you can run the project with this command
```
python manage.py runserver
```
