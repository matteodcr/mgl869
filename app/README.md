# Simple python server
Exposes a simple ML model for prediction using flask.

## Run localy
**Python 3.12 required**

### Without a virtual environement
```bash
pip install -r requirements.txt
flask --app app/api run
```

### With a virtual environement
```bash
pipenv install -r requirements.txt
pipenv run flask --app app/api run
```

### Using docker
```bash
docker build -f app/Dockerfile --tag 'simplepythonserveurmgl869' .
docker run -p 5000:5000 -i 'simplepythonserveurmgl869' 
```