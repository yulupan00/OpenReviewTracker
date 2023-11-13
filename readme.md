# OpenReview Tracker
Explore OpenReview for all the venues hosted on the site.

Run ```pip install -r requirements.txt``` to install openreview api for python

Some functinalities in util:
| Function | Description |
| --- | --- |
| getAllVenues | Get all the venue names from the OpenReview API |
| mostHostedVenue | Get top 20 most hosted venue domain such as NeurIPS.cc |
| getAbstractWithRating | Get the venue's submission and pair each abstract with the mean rating from every reviewer |
| topSubmission | Get the top 20 submissions from that certain conference |
| toLLMTrainingData | Convert the venue data to a JSON file with following format: {'text': "### Human: Rate this abstract ...}### Assistant: I would rate this (mean_dating)!"} |
| getPaperWithCitation | Using scholarly to get the citation of papers from a venue (Not working)|
| plotDecision | Get the decision and rating plot|

### TODO
- [ ] Fix getPaperWithCitation to not get blocked and extract all paper from the venue
- [ ] Use the toLLMTrainingData and train a custom Llama to rate an abstract

Example most hosted venue plot:

![Alt text](images/MostHostedVenue.png)

Example decision with rating plot:
![Alt text](images/decision_ICLR.cc_2018_Conference.png)
![Alt text](images/decision_ICLR.cc_2021_Conference.png)