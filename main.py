import util

util.getAllVenues() #Get all the venues and save to venue.csv file
util.mostHostedVenue() #Get most hosted venue domain such as NeurIPS.cc

toy_venue = "ICLR.cc/2018/Conference"
util.getAbstractWithRating(toy_venue) #Get the venue's submission and pair each abstract with the mean rating from every reviewer
util.topSubmission(toy_venue) #Get the top 20 submissions from that certain conference