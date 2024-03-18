# Streaming Query Tester with Proton

An example app to tinker with Proton.

# Requirements

* Proton (brew install proton)
* Redis for Pubsub via Flask (brew install redis)
* Python 3.12
* Flask with Gunicorn and gevent for the Server Sent Events

# Get Started

Clone the repo and run:

```
cd streamingqueries
python -m venv venv
source venv/bin/activate
pip install proton-driver flask gunicorn gevent redis
proton server start
```

Separately start the flask app with gunicorn

```
cd streamingqueries
gunicorn -w 4 -k gevent app:app
```

Then browse to http://127.0.0.1:8000/