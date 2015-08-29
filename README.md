Gitbot
======

This is a slack bot that listens to gitlab and github web hooks in order to communicate the events to the appropriate slack channel.

Among other things this bots keeps track of commit statistics and notifies them in a periodical manner to the #general channel.

Dependencies
------------

* [Flask](http://flask.pocoo.org/)
* [Redis](https://pypi.python.org/pypi/redis)
* [Slacker](https://github.com/os/slacker)

For all requirements see the file [requirements.txt](requirements.txt)


Usage
-----

* Clone the repo

```$ git clone https://github.com/niclabs/gitbot.git```

* Initialize the virtual environment (python 2.7+)

```
$ virtualenv venv --distribute --no-site-packages
$ source venv/bin/activate
```

* Download required packages

```
(venv)$ pip install -r requirements.txt
```

* Run the server
```
(venv)$ python manage.py runserver
```

The server should now be running on [localhost:5000](http://localhost:5000)
