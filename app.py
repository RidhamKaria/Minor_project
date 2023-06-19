from flask import Flask, render_template, request, redirect, session
from ToxiCR import ToxiCR
import json
import requests
import pandas as pd
from bs4 import BeautifulSoup
import snscrape.modules.twitter as sntwitter
from googleapiclient import discovery
import json

app = Flask(__name__)


@app.route('/', methods=['GET'])
def greet():
    return render_template("form.html")


@app.route('/text', methods=['GET', 'POST'])
def input():
    if (request.method == "GET"):
        return json.dumps({"error": "Invalid method. Only POST method is accepted."})
    toxicClassifier = ToxiCR(ALGO="RF", count_profanity=True, remove_keywords=False, split_identifier=False,
                             embedding="tfidf", load_pretrained=True)
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36"
    }
    out_dict = dict()
    # r = requests.get(base_url_amz+id+"?pageNumber=1",headers=headers)
    # if(r.ok):
    #     soup = BeautifulSoup(r.text, 'html.parser')
    #     res = soup.findAll('span',{'class':'review-text'})
    #     input = [i.get_text() for i in res]
    #     toxicClassifier.init_predictor()
    #     if (len(input)== 0):
    #         return {"error": "Invalid query size"}
    #     results = toxicClassifier.get_toxicity_probability(input)
    #     for i in range(len(input)):
    #         out_dict[input[i]] = str("toxic" if results[i][0]==1 else "non-toxic")
    # elif(request.form['options']=='Twitter'):
    if (not request.files['csv_file']):
        return "No files selected.."
    name = request.files['csv_file']
    frame = pd.read_csv(name)
    input = frame['text'].tolist()
    toxicClassifier.init_predictor()
    if (len(input) == 0):
        return {"error": "Invalid query size"}
    results = toxicClassifier.get_toxicity_probability(input)
    for i in range(len(input)):
        out_dict[input[i]] = str("toxic" if results[i]
                                 [0] == 1 else "non-toxic")
    return render_template("form.html", data=out_dict)


@app.route('/pers', methods=['POST'])
def analyse():
    input_text = request.json["data"]

    API_KEY = 'AIzaSyA_CfXPoBVOZLI9uLqKtWURPQAuDVWj-Mg'

    client = discovery.build(
        "commentanalyzer",
        "v1alpha1",
        developerKey=API_KEY,
        discoveryServiceUrl="https://commentanalyzer.googleapis.com/$discovery/rest?version=v1alpha1",
        static_discovery=False,
    )

    analyze_request = {
        'comment': {'text': input_text},
        'requestedAttributes': {'TOXICITY': {}, "UNSUBSTANTIAL": {}}
    }

    response = client.comments().analyze(body=analyze_request).execute()
    # if(response['attributeScores']['TOXICITY']['summaryScore']['value'] > 0.75):
    #     return "Warning! your content might violet some toxicity policy so kindly rephrase your sentence."
    # return "Your content is safe from any toxicity."
    return str(response['attributeScores']['TOXICITY']['summaryScore']['value'])
    # if(response['attributeScores']['TOXICITY']['summaryScore']['value']>0.75):
    #     return str(1)
    # return str(0)

@app.route('/export',methods=['POST'])
def export():
    input=request.json['data']
    toxicClassifier = ToxiCR(ALGO="RF", count_profanity=True, remove_keywords=False, split_identifier=False,
                             embedding="tfidf", load_pretrained=True)
    toxicClassifier.init_predictor()
    results = toxicClassifier.get_toxicity_probability([input])
    return str(results[0][0])