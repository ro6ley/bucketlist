[![Build Status](https://travis-ci.org/NaiRobley/bucketlist.svg?branch=develop)](https://travis-ci.org/NaiRobley/bucketlist)
[![Coverage Status](https://coveralls.io/repos/github/NaiRobley/bucketlist/badge.svg?branch=develop)](https://coveralls.io/github/NaiRobley/bucketlist?branch=develop)

# Project - The BucketList

According to Merriam-Webster Dictionary, ​a Bucket List is a list of things that one has not done
before but wants to do before dying ​.
This project is an API for an online Bucket List service using Flask.



## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites

* Python3.6
* PostgreSQL

The requirements are in the `requirements.txt` file



### Installing

Clone the repo:

For HTTPS
```
$ git clone https://github.com/NaiRobley/bucketlist.git
```
For SSH
```
$ git clone git@github.com:NaiRobley/bucketlist.git
```

Change Directory into the project folder
```
$ cd bucketlist
```

Create a virtual environment with Python 3.6
```
$ virtualenv --python=python3.6 yourenvname
```

Activate the virtual environment you have just created
```
$ source yourenvname/bin/activate
```

Install the application's dependencies from requirements.txt to the virtual environment
```
$ (yourenvname) pip install -r requirements.txt
```

Create the database:
For Postgres
```
$ createdb flask_api
$ createdb test_db
```

For other databases modify the `instance/config.py`

Migrations:
```
$ (yourenvname) python manage.py db init
$ (yourenvname) python manage.py db migrate
$ (yourenvname) python manage.py db upgrade
```

Run the tests to ensure everything is in order:
```
$ (yourenvname) nosetests -v
```

Run the application:
```
$ (yourenvname) python run.py
```


### Specifications for the API
```
ENDPOINT                                         FUNCTIONALITY                          PUBLIC ACCESS

POST    /auth/login/                             Logs a user in                         TRUE
POST    /auth/register/                          Register a user                        TRUE
POST    /bucketlists/                            Create a new bucket list               FALSE
GET     /bucketlists/                            List all the created bucket lists      FALSE
GET     /bucketlists/<id>/                       Get single bucket list                 FALSE 
PUT     /bucketlists/<id>/                       Update this bucket list                FALSE
DELETE  /bucketlists/<id>/                       Delete this single bucket list         FALSE
POST    /bucketlists/<id>/items/                 Create a new item in bucket list       FALSE
PUT     /bucketlists/<id>/items/<item_id>/       Update a bucket list item              FALSE
DELETE  /bucketlists/<id>/items/<item_id>/       Delete an item in a bucket list        FALSE
```

## Interacting with the API

### CURL

To interact with the API via CURL
```

```

### Postman

To interact with the API using Postman
```

```

**Contributions are highly welcomed and appreciated**

## Libraries
[Flask](http://flask.pocoo.org/) - Flask is a microframework for Python based on Werkzeug, Jinja 2 and good intentions. 

[SQLAlchemy](https://www.sqlalchemy.org/) - SQLAlchemy is the Python SQL toolkit and Object Relational Mapper that gives application developers the full power and flexibility of SQL.


## Authors

* **Robley Gori**


## License


## Acknowledgments

* The Internet
