#!/usr/bin/env python

############################################################################
#
# This script produces the history plot graphics for the median number of
# Clinton electoral votes as estimated on each day of the campgain season
# from May 22 to the present. It also includes the 95% confidence interval.
# These quantities are calculated by the MATLAB script EV_estimator.m. In
# stand-alone operation, the plot is drawn by the MATLAB script
# EV_history_plot.m, however we re-draw the plot here using Python's
# matplotlib for improved display on the web. (MATLAB also has a bug which
# causes it to crash when attempting to plot this graphic in an automated
# environment without a display.)
#
# Author: Andrew Ferguson <adferguson@alumni.princeton.edu>
#
# Script written for election.princeton.edu run by Samuel S.-H. Wang under
# noncommercial-use-only license:
# You may use or modify this software, but only for noncommericial purposes.
# To seek a commercial-use license, contact sswang@princeton.edu
#
# Update History:
#    Aug 19, 2012 -- moved to GitHub; future updates in commit messages
#    Aug 12, 2012 -- Add support for comments in csv file; CI more translucent
#    Jul  8, 2012 -- Add year to large chart
#    Jul  7, 2012 -- Update for 2012
#    Oct  7, 2008 -- Highlight edge of 95% CI with green
#
############################################################################

import time 

import matplotlib
matplotlib.use('Agg')
from pylab import *
import datetime

def campaign_day(day):
    jan_one = datetime.date(datetime.date.today().year, 1, 1)
    return ((day - jan_one).days + 1)


campaign_start = campaign_day(datetime.date(2016, 5, 22))

hfile = open("EV_estimate_history.csv")
ev_hist = array([[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]])

# Build a numpy array from the CSV file, except for the last three entries
for line in hfile:
    if line[0] != '#':
        ev_hist = append(ev_hist, [map(int, line[:-1].split(",")[:13])], axis=0)

hfile.close()
ev_hist = delete(ev_hist, 0, 0)

#    Each line of EV_estimate_history should contain:
#    1 value - date code
#    2 values - medianEV for the two candidates, where a margin>0 favors the
#			first candidate (in our case, Clinton);
#    2 values - modeEV for the two candidates;
#    3 values - assigned (>95% prob) EV for each candidate, with a third entry
#			for undecided;
#    4 values - confidence intervals for candidate 1's EV: +/-1 sigma, then
#			95% band; and
#    1 value - number of state polls used to make the estimates.
#    1 value - metamargin

dates = ev_hist[:,0]
medianDem = ev_hist[:,1]
modeDem = ev_hist[:,3]
lowDem95 = ev_hist[:,10]
highDem95 = ev_hist[:,11]

############################################################################
#
# Thumbnail-size graphic, 200px wide, for the right sidebar display
# throughout the blog.
#
############################################################################

subplot(111, axisbelow=True, axisbg='w')

plot((campaign_start-2, 320), (269, 269), '-r', linewidth=1)

yticks(arange(160, 420, 20))
# TODO(adf): construct programatically (month starts after campaign_start)
xticks([campaign_start, 153, 183, 214, 245, 275, 306],
		('      May','          Jun',
		 '          Jul','          Aug','          Sep',
		 '          Oct','        Nov'), fontsize=19)


grid(color='#aaaaaa')

title("Median EV estimator", fontsize=27, fontweight='bold')
ylabel("Clinton EV", fontsize=25, fontweight='bold')

plot(dates, medianDem, '-k', linewidth=2)

xs, ys = poly_between(dates, lowDem95, highDem95)
fill(xs, ys, '#222222', alpha=0.075, edgecolor='none')

#
# hurricane tracker prediction ... functions would be nice :-(
#
pfile = open("EV_prediction.csv")
prediction = {}

(prediction["1sigma_low"], prediction["1sigma_high"], prediction["2sigma_low"],
        prediction["2sigma_high"]) = map(int, pfile.read().strip().split(","))

pfile.close()

election = campaign_day(datetime.date(2016, 11, 8))

low = min(prediction["2sigma_low"], lowDem95[-1])
high = max(prediction["2sigma_high"], highDem95[-1])
xs, ys = poly_between([dates[-1], election-2], [lowDem95[-1], low], [highDem95[-1], high])
fill(xs, ys, 'yellow', alpha=0.3, edgecolor='none')
xs, ys = poly_between([election-2, election], [low, low], [high, high])
fill(xs, ys, 'yellow', edgecolor='none')

low = prediction["1sigma_low"]
high = prediction["1sigma_high"]
xs, ys = poly_between([dates[-1], election-2], [medianDem[-1], low], [medianDem[-1]+1, high])
fill(xs, ys, 'red', alpha=0.2, edgecolor='red')
xs, ys = poly_between([election-2, election], [low, low], [high, high])
fill(xs, ys, 'red', edgecolor='none')
#
# end hurricane tracker prediction
#

xlim(campaign_start, 320)
ylim(197, 423)

show()
savefig(open('EV_history-200px.png', 'w'), dpi=25)

clf()

############################################################################
#
# Larger graphic, 500px wide, designed to fit in the center content column.
#
############################################################################

subplot(111, axisbelow=True, axisbg='w')

plot((campaign_start-2, 320), (269, 269), '-r', linewidth=1)

yticks(arange(160, 420, 20))
# TODO(adf): construct programatically (month starts after campaign_start)
xticks([campaign_start,153,183,214,245,275,306],
		('        May','            Jun',
		 '            Jul','            Aug','            Sep',
		 '            Oct','        Nov'), fontsize=16)


grid(color='#aaaaaa')

title("Median EV estimator", fontsize=18,
		fontweight='bold')
ylabel("Clinton EV",fontsize=16)
text(campaign_start+3, 172, time.strftime("%d-%b-%Y %I:%M%p %Z"), fontsize=14)
text(campaign_start+3, 159, "election.princeton.edu", fontsize=14)

plot(dates, medianDem, '-k', linewidth=2)

xs, ys = poly_between(dates, lowDem95, highDem95)
fill(xs, ys, '#222222', alpha=0.075, edgecolor='none')

#
# hurricane tracker prediction
#
election = campaign_day(datetime.date(2016, 11, 8))

low = min(prediction["2sigma_low"], lowDem95[-1])
high = max(prediction["2sigma_high"], highDem95[-1])
xs, ys = poly_between([dates[-1], election-2], [lowDem95[-1], low], [highDem95[-1], high])
fill(xs, ys, 'yellow', alpha=0.3, edgecolor='none')
xs, ys = poly_between([election-2, election], [low, low], [high, high])
fill(xs, ys, 'yellow', edgecolor='none')

low = prediction["1sigma_low"]
high = prediction["1sigma_high"]
xs, ys = poly_between([dates[-1], election-2], [medianDem[-1], low], [medianDem[-1]+1, high])
fill(xs, ys, 'red', alpha=0.2, edgecolor='red')
xs, ys = poly_between([election-2, election], [low, low], [high, high])
fill(xs, ys, 'red', edgecolor='none')

text(312, 327, "Prediction", fontsize=14, rotation='270')
#
# end hurricane tracker prediction
#

## Election Day indicator
day=campaign_day(datetime.date(2016, 11, 8))
axvline(x=day, linestyle='--', color='black')

xlim(campaign_start, 320)
ylim(197, 423)

show()
savefig(open('EV_history-unlabeled.png', 'w'), dpi=62.5, facecolor='#fcfcf4',
		edgecolor='#fcfcf4')

## Annotations 


## End Annotations 

show()
savefig(open('EV_history.png', 'w'), dpi=62.5, facecolor='#fcfcf4',
		edgecolor='#fcfcf4')

show()
savefig(open('EV_history-full_size.png', 'w'), facecolor='#fcfcf4',
		edgecolor='#fcfcf4')
