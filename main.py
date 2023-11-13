from util import *

getAllVenues() #Get all the venues and save to venue.csv file
mostHostedVenue() #Get most hosted venue domain such as NeurIPS.cc

toy_venue = "ICLR.cc/2018/Conference" #Change to any venue from the getAllVenues() result

getAbstractWithRating(toy_venue) #Get the venue's submission and pair each abstract with the mean rating from every reviewer
topSubmission(toy_venue) #Get the top 20 submissions from that certain conference
plotDecision(toy_venue) #Get the decision and rating plot


#getPaperWithCitation(toy_venue)