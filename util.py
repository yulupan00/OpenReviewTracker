import os
import openreview
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import time
from tqdm import tqdm

client = openreview.api.OpenReviewClient(baseurl='https://api.openreview.net')

def getAllVenues():
    venues = client.get_group(id='venues').members
    df = pd.DataFrame(venues, columns=["venue"])
    df.to_csv("venue.csv", index=False)

def mostHostedVenue(df = None, plot = False):
    if df is None:
        df = pd.read_csv("venue.csv")
    df['venue_domain'] = df['venue'].apply(lambda x: x.split('/')[0])
    popularVenue = df['venue_domain'].value_counts().head(20)
    if plot:
        plt.figure(figsize=(10, 6))
        popularVenue.plot(kind='bar', color='skyblue')
        plt.xlabel('Venue Domain')
        plt.ylabel('Count')
        plt.title('Top 20 Most Hosted Venues')
        plt.xticks(rotation=45, ha='right') 
        plt.tight_layout()
        plt.savefig("MostHostedVenue.png")
        #plt.show()
    return popularVenue

def getAbstractWithRating(venue):
    submissions = client.get_all_notes(invitation = f"{venue}/-/Blind_Submission", details='directReplies')
    data = []
    for submission in tqdm(submissions):
        title = submission.content['title']
        abstract = submission.content['abstract'].replace("\n", "")
        scores = []
        for reviewer in submission.details['directReplies']:
            try:
                scores.append(int(reviewer['content']['rating'].split(':')[0]))
            except:
                #tqdm.write(f"Rating Missing for {title}!")
                continue
        mean_score = np.mean(scores)
        data.append([title, abstract, mean_score])

    df = pd.DataFrame(data, columns=["title", "abstract", "mean_rating"])
    file_path = venue.replace('/', "_")
    df.to_csv(f"{file_path}_data.csv", index=False)

def topSubmission(venue):
    file_path = venue.replace('/', "_")
    if not os.path.exists(f"{file_path}_data.csv"):
        getAbstractWithRating(venue)
    df = pd.read_csv(f"{file_path}_data.csv")
    df_top = df.sort_values(by='mean_rating', ascending=False).head(20)
    print(f"Top Submissions in {venue}:")
    for _, row in df_top.iterrows():
        print("{}, Avearge Rating: {} ".format(row['title'], row['mean_rating']))

def toLLMTrainingData(df):
    import json
    output_dict_list = []
    for _, row in df.iterrows():
        output_dict_list.append({'text': f"### Human: Rate this abstract {row['abstract']}### Assistant: I would rate this {row['mean_rating']}!"})

    filename = 'output_dict_list.json'
    with open(filename, 'w') as json_file:
        json.dump(output_dict_list, json_file, indent=2)
