# Copyright 2018 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# [START gae_python37_app]
from flask import Flask, render_template
import numpy as np
from datascience import Table

# If `entrypoint` is not defined in app.yaml, App Engine will look for an app
# called `app` in `main.py`.
from willitpass_funcs import predict_sentiment, model_setup

app = Flask(__name__)


@app.route('/')
def hello():
    """Return the landing page of Will It Pass?"""
    return render_template('index.html')

@app.route('/results/')
@app.route('/results/<string:selected_states>/<string:words>')
def results(selected_states="none", words="none"):
    if selected_states == "none" or words == "none":
        return "Make sure you selected your state(s) AND submitted a topic of interest. Press the back button to retry."
    else:
        print("Calculating...")
        states = selected_states.replace(","," ")

        #Do some magic here to correspond states with senator
        #models = np.where(senators in model)
        #models is an array of the filenames of modles
        #word2ids is an array of the filenames of word2ids
        senators = []
        sen_state = []
        models = ["app/models/model_architecture_set_0.json", "app/models/model_architecture_set_1.json"]
        word2ids = ["app/models/word2id_set_0.json", "app/models/word2id_set_1.json"]
        weights = ['app/models/model_weights_set_0.h5', 'app/models/model_weights_set_1.h5']
        k = len(models)
        sentiments = []
        for i in range(k):
            (model, word2id) = model_setup(models[i], word2ids[i], weights[i])
            sentiments.append(predict_sentiment(words, model, word2id))
            print(i)

        table_results = Table().with_columns("Senators", senators, "State", sen_state, "Sentiment", sentiments)
        text_results = table_results.as_text()

        return render_template("results.html", selected_states=selected_states, words=words, result=text_results)


if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)
# [END gae_python37_app]
