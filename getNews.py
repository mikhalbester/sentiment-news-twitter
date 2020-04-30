# Look at relationship between news headlines and social media sentiments

import requests
import pandas as pd
import numpy as np
import json
import datetime
import pickle

from ibm_watson import ToneAnalyzerV3
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

from google.cloud import language
from google.cloud.language import enums
from google.cloud.language import types
from google.oauth2 import service_account

from newsapi import NewsApiClient

authenticator = IAMAuthenticator('oNNQGIwhvTsrs7niTmPbnqPs3EcXnj4elwi0HEucImz6')
tone_analyzer = ToneAnalyzerV3(
    version='2017-09-21',
    authenticator=authenticator
)

tone_analyzer.set_service_url('https://api.us-south.tone-analyzer.watson.cloud.ibm.com/instances/dbc882eb-4a69-4925-bf1b-77438b94206e/v3/tone?version=2017-09-21&sentences=false')

newsapi = NewsApiClient(api_key='ee504f059b1c485fbbf124453ecd2eae')

from_date = (datetime.date.today()-datetime.timedelta(days=7)).strftime('%Y-%m-%d')

headlines = []
for i in range(1,100):
    headlines += newsapi.get_everything(
    q='coronavirus OR covid-19 OR covid',
    language='en',
    page_size=100,
    from_param=from_date,
    sort_by='popularity')['articles']
len(headlines)

def parseResponse(response):
    rows = []
    columns = ['source','author','title','description','urlToImage','url','publishedAt','content']
    for article in response:
        rows.append([article.get(key) for key in columns])
    df = pd.DataFrame(rows, columns=columns)
    df['sourceId'] = df['source'].map(lambda x: x['id'])
    df['sourceName'] = df['source'].map(lambda x: x['name'])
    df.drop('source',axis=1, inplace=True)
    return(df)
response_pop7
df = parseResponse(headlines)
df
df.to_pickle('df.pickle')

text=df.iloc[21]['title']
tone_analysis = tone_analyzer.tone({'text': text},
    content_type='application/json').get_result()
print(json.dumps(tone_analysis, indent=2))
text

def getSentiment(text):
    client = language.LanguageServiceClient.from_service_account_file('applied-causality-website-bf1f5a18882b.json')
    document = types.Document(
        content=text,
        type=enums.Document.Type.PLAIN_TEXT)
    sentiment = client.analyze_sentiment(document=document).document_sentiment
    return(sentiment.score)

df['titleSentiment']=df['title'].apply(getSentiment)
df['descriptionSentiment']=df['description'].apply(getSentiment)
df['sentimentMean']=df[["titleSentiment",'descriptionSentiment']].mean(axis=1)
df['titleSentiment'].sample(5)
df.to_pickle('df_sentiment.pickle')


import plotly.express as px
fig = px.violin(df, x='sourceName', y='titleSentiment', box=True, hover_data=['title'], points='all', width=2000, height=600)
fig.show()
