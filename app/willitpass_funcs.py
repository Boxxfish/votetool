from keras.models import model_from_json
from tensorflow import keras
from tensorflow.python.keras import backend as k
import tensorflow as tf
from tensorflow.keras.preprocessing import sequence
from tensorflow.keras import Sequential
from tensorflow.keras.layers import Embedding, LSTM, Dense, Dropout
import json
from tensorflow.python.keras.backend import set_session
from tensorflow.python.keras.models import load_model
# graph = tf.get_default_graph()

graph = tf.compat.v1.get_default_graph()
sess = tf.get_default_session()

def model_setup(model_filename, word2id_filename, weights_filename):

	# Model reconstruction from JSON file
	with open(model_filename, 'r') as f:
		model = tf.keras.models.model_from_json(f.read())

	# Load weights into the new model
	model.load_weights(weights_filename)

	model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

	# Load word2id trained
	with open(word2id_filename, 'r') as fp:
		word2id = json.load(fp)

	return model, word2id

def predict_sentiment(text, model, word2id, max_words=1000):
	text = str(text)
	text = text.split(" ")
	text = [word.lower() for word in text]
	for word in text:
		if word in word2id:
			text.append(word2id[word])
		else:
			text.append(len(word2id.keys()))
	text = sequence.pad_sequences([text], maxlen=max_words)
	global sess
	text_pred = None
	global graph
	with graph.as_default():
		text_pred = model.predict_proba(text)
	return text_pred

# tf_config = some_custom_config
    # sess = tf.Session(config=tf_config)
    # graph = tf.get_default_graph()
    # with session.graph.as_default():
    #     k.backend.set_session(session)
    #     with graph.as_default():