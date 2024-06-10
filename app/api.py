import atexit
from flask import Flask, Response, abort, request, render_template
import json
import pandas as pd
import weakref

from manage import Model, ModelManager



app = Flask(__name__)

models = ModelManager("app/models")
atexit.register(lambda: models.close())


@app.get("/")
def root():
    return render_template("form.html")


@app.post("/predict")
def predict():
    model = models.active_model

    if model is None:
        abort(503, description=f"No model is active right now")

    if model.estimator is None:
        model.load()

    #try:
    form = pd.DataFrame({k: [v] for k, v in request.form.items()})[model.estimator["input_columns"]]
    form = form.astype(model.estimator["input_dtypes"])
    #except:
    #    abort(400) # Bad request if field is missing

    prediction = model.estimator["estimator"].predict(form)

    return Response(json.dumps({
        'prediction': prediction[0],
        'model_name': model.name,
        'model_digest': model.digest,
    }), mimetype="application/json")


# This is a bad and unsafe way to authenticate users but I want to keep things simple for this project
def assert_local():
    if request.access_route[-1] != '127.0.0.1':
        abort(403, description="The server can only be managed from 127.0.0.1")


@app.get("/manage")
def manage_root():
    assert_local()
    return render_template("manage.html", models=models.loaded_models, active_model=models.active_model)


@app.post("/manage")
def manage_post():
    assert_local()
    loaded_models = models.loaded_models
    model_name = request.form["name"]
    model = next(filter(lambda m: m.name == model_name, loaded_models), None)

    if model is not None:
        if request.form["action"] == "activate":
            models.active_model = model
        else:
            models.active_model = None

    return render_template("manage.html", models=loaded_models, active_model=models.active_model)
