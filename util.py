import os
import openreview
import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
import plotly.express as px

from scholarly import scholarly, ProxyGenerator

import random
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
            if 'decision' in reviewer['content'].keys():
                decision = reviewer['content']['decision']
            if 'rating' in reviewer['content'].keys():
                scores.append(int(reviewer['content']['rating'].split(':')[0]))
        mean_score = np.mean(scores)
        data.append([title, abstract, mean_score, decision])

    df = pd.DataFrame(data, columns=["title", "abstract", "mean_rating", "decision"])
    file_path = venue.replace('/', "_")
    df.to_csv(f"{file_path}_data.csv", index=False)

def topSubmission(venue):
    df = readVenueData(venue)
    df_top = df.sort_values(by='mean_rating', ascending=False).head(20)
    print(f"Top Submissions in {venue}:")
    for _, row in df_top.iterrows():
        print("{}, Avearge Rating: {} ".format(row['title'], row['mean_rating']))
    return df_top

def plotDecision(venue):
    df = readVenueData(venue)
    rating_ranges = np.arange(0, 10 + 1, 1)

    rating_dict = [f"{start}-{end}" for start, end in zip(rating_ranges, rating_ranges[1:])]
    accept_counts = np.zeros(10)
    reject_counts = np.zeros(10)

    for _, row in df.iterrows():
        try:
            if "accept" in row["decision"].lower():
                accept_counts[int(row["mean_rating"])] +=1
            else:
                reject_counts[int(row["mean_rating"])] +=1
        except:
            continue

    fig, ax = plt.subplots(figsize=(10, 6))
    bar_width = 0.4
    opacity = 0.7

    bar_positions_accept = range(len(rating_dict))
    bar_positions_reject = [pos + bar_width for pos in bar_positions_accept]

    plt.bar(bar_positions_accept, accept_counts, bar_width, alpha=opacity, color='blue', label='Accept')
    plt.bar(bar_positions_reject, reject_counts, bar_width, alpha=opacity, color='red', label='Reject')

    ax.set_xlabel('Mean Rating Range')
    ax.set_ylabel('Paper Count')
    ax.set_title(f'Accept and Reject Counts {venue}')
    ax.set_xticks([pos + bar_width / 2 for pos in bar_positions_accept])
    ax.set_xticklabels(rating_dict)
    ax.legend()

    for index, (accept, reject) in enumerate(zip(accept_counts, reject_counts)):
        if accept > 0: 
            plt.text(bar_positions_accept[index] + bar_width / 2, accept, int(accept), ha='right', va='bottom', color='black')
        if reject > 0: 
            plt.text(bar_positions_reject[index] + bar_width / 2, reject, int(reject), ha='right', va='bottom', color='black')

    plt.tight_layout()
    file_name = venue.replace('/', "_")
    plt.savefig(f'decision_{file_name}.png')
    #plt.show()
    

def toLLMTrainingData(df):
    import json
    output_dict_list = []
    for _, row in df.iterrows():
        output_dict_list.append({'text': f"### Human: Rate this abstract {row['abstract']}### Assistant: I would rate this {row['mean_rating']}!"})

    filename = 'output_dict_list.json'
    with open(filename, 'w') as json_file:
        json.dump(output_dict_list, json_file, indent=2)

def getPaperCitationCount(title):
    search_query = scholarly.search_pubs(title)
    try:
        return next(search_query)['num_citations']
    except:
        tqdm.write("Error getiing the citation! {}".format(title))
        return -1

def getPaperWithCitation(venue):
    file_path = venue.replace('/', "_")
    if not os.path.exists(f"{file_path}_data.csv"):
        getAbstractWithRating(venue)
    df = pd.read_csv(f"{file_path}_data.csv")
    df['citation'] = np.nan
    for index, row in tqdm(df.iterrows(), total=df.shape[0]):
        count = getPaperCitationCount(row['title'])
        time.sleep(random.uniform(1, 5)) #Try sleeping some time to not get blocked
        if count > -1:
            df.at[index,'citation'] = count
            tqdm.write("{}: Citation count {}".format(row['title'], count))
    df.to_csv(f"{file_path}_data_citation.csv", index=False)    

def getPaperCitation(df_top):
    df_top['citation'] = np.nan
    for index, row in tqdm(df_top.iterrows(), total=df_top.shape[0]):
        count = getPaperCitationCount(row['title'])
        time.sleep(random.uniform(1, 5)) #Try sleeping some time to not get blocked
        if count > -1:
            df_top.at[index,'citation'] = count
            tqdm.write("{}: Citation count {}".format(row['title'], count))
    
    fig = px.scatter(df_top, x="mean_rating", y="citation", text="title")
    fig.update_traces(marker={'size': 15}, textposition='top center', hovertemplate="%{text}<extra></extra>")
    fig.show()

def readVenueData(venue):
    file_path = venue.replace('/', "_")
    if not os.path.exists(f"{file_path}_data.csv"):
        getAbstractWithRating(venue)
    df = pd.read_csv(f"{file_path}_data.csv")
    return df
    
