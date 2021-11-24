import pandas as pd
# import numpy as np
# import dill
import os
import flask
import logging
from logging.handlers import RotatingFileHandler
from time import strftime
from pipeline.pipeline import Pipeline

# initialize our Flask application and the model
app = flask.Flask(__name__)
# model = None

handler = RotatingFileHandler(filename='app.log', maxBytes=100000, backupCount=10)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(handler)


# def load_model(model_path):
# 	# load the pre-trained model
# 	global model
#
# 	with open(model_path, 'rb') as f:
# 		model = dill.load(f)
# 	print(model)


modelpath = "dill_clf_model.dill"
# load_model(modelpath)
model = Pipeline(modelpath)
print(model)


@app.route("/", methods=["GET"])
def general():
	return """Welcome to fraudelent prediction process. Please use 'http://<address>/predict' to POST"""


@app.route("/predict", methods=["POST"])
def predict():
	# initialize the data dictionary that will be returned from the
	# view
	data = {"success": False}
	dt = strftime("[%Y-%b-%d %H:%M:%S]")
	# ensure an image was properly uploaded to our endpoint
	if flask.request.method == "POST":

		id, x = [], []
		request_json = flask.request.get_json()
		if request_json["id"]:
			id = request_json['id']

		if request_json["x"]:
			x = request_json['x']

		logger.info(f'{dt} Data: id={id}, x={x}')
		try:
			preds, diagnosis, pattern_per_5minute = model.predict(pd.DataFrame({"id": id, "x": x}))
		except AttributeError as e:
			logger.warning(f'{dt} Exception: {str(e)}')
			data['predictions'] = str(e)
			data['diagnosis'] = str(e)
			data['pattern_per_5minute'] = str(e)
			data['success'] = False
			return flask.jsonify(data)

		data["predictions"] = list(preds) # list
		data['diagnosis'] = diagnosis # dict
		data['pattern_per_5minute'] = pattern_per_5minute # dict
		# indicate that the request was a success
		data["success"] = True

	# return the data dictionary as a JSON response
	return flask.jsonify(data)

# if this is the main thread of execution first load the model and
# then start the server
if __name__ == "__main__":
	print(("* Loading the model and Flask starting server..."
		"please wait until server has fully started"))
	port = int(os.environ.get('PORT', 8180))
	app.run(host='0.0.0.0', debug=True, port=port)
