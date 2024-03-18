# Streaming Query Tester with Proton

An example app to tinker with Proton.

# Requirements

* Proton (brew install proton)
* Flask (brew install flask) with Gunicorn and gevent for the Server Sent Events
* Python 3.12

# Get Started

Clone the repo and run:

```
cd streaming
python -m venv venv
source venv/bin/activate
pip install proton-driver
pip install gunicorn
pip install gevent
proton server start
```

Separately start the flask app with gunicorn

```
gunicorn -w 4 -k gevent app:app
```

Then browse to http://127.0.0.1:8000/