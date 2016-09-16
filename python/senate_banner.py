#!/usr/bin/python
# -*- coding: utf-8 -*-

############################################################################
#
# This script produces the display at the top of the blog of the current
# median electoral votes for each candidate.
#
# Author: Mark Tengi <markat@princeton.edu>
# Originally by: Andrew Ferguson <adferguson@alumni.princeton.edu>
#
# Script written for election.princeton.edu run by Samuel S.-H. Wang under
# noncommercial-use-only license:
# You may use or modify this software, but only for noncommericial purposes.
# To seek a commercial-use license, contact sswang@princeton.edu
#
############################################################################

import time
import csv
import sys

# Take a float 0 < prob < 1 and return a string rounded appropriately
def format_control_prob(prob, percentage=True):
    if prob <= 0.9:
        rounded = int(round(prob * 20) * 5) # round to nearest 5%
        #rounded = int(round(prob * 100)) # NEW round to nearest 1% instead
        return '%s' % rounded if percentage else '.%s' % rounded
    elif prob <= 97.0:
        rounded = int(round(prob * 100)) # round to nearest 1%
        return "%s" % rounded if percentage else '.%s' % rounded
    else:
        rounded = int(round(prob * 1000)) /10.0 # round to nearest 0.1%
        return "%.1f" % rounded if percentage else '.%s' % int(rounded * 10)

def main(infile, nov_infile, outfile):

    bottom_url = '/2014/09/30/pec-switching-as-planned-to-short-term-forecast/'
    error = 2.5
    error_url = '/2014/10/17/is-ebola-diverting-voter-attention/'

    ## Estimated electoral votes and the current meta-margin

    values = csv.reader(infile).next() # get the first (and only) row
    infile.close()

    time_str = time.strftime("%B %d, %Y %I:00 %p")

    dem_seats = int(values[0])
    gop_seats = 100 - dem_seats
    metamargin = float(values[10])
    metamargin_str = ('D' if metamargin > 0 else 'R') + ' %+.1f%%' % abs(metamargin)

    control_prob_str = format_control_prob(float(values[2]))

    november_values = csv.reader(nov_infile).next()
    november_pred = float(november_values[1]) * .01 # Change range to 0 <= x <= 1
    november_ctrl_prob = format_control_prob(november_pred)
    november_pred_str = '%s±15%%' % november_ctrl_prob
    november_pred_range = '%d%% &mdash; %d%%' % (int(november_ctrl_prob) - 15, int(november_ctrl_prob) + 15)
    #november_pred_str = str(round(november_pred, 1))
    november_mm = round(float(november_values[2]), 1)
    november_mm_str = "%s%+.1f±%.1f%% (1 sigma CI)" % (("R" if november_mm < 0 else "D"), abs(november_mm), error)
    low_end = '%s+%.1f%%' % ('R' if november_mm - error < 0 else 'D', abs(november_mm - error))
    high_end = '%s+%.1f%%' % ('R' if november_mm + error < 0 else 'D', abs(november_mm + error))
    november_mm_range = '%s &mdash; %s' % (low_end, high_end)

    ## Write the website header

    outfile.write('\t<li><a href="/todays-senate-seat-count-histogram/">Senate current conditions, %s:</a></li>\n' % time_str)
    outfile.write('\t<li><a href="/todays-senate-seat-count-histogram/" style="color: blue">Dem+Ind:</a><span style="color: blue"> %s</span></li>\n' % dem_seats)
    outfile.write('\t<li><a href="/todays-senate-seat-count-histogram/" style="color: red">GOP:</a><span style="color: red"> %s</span></li>\n' % gop_seats)

    outfile.write('\t<li><a href="/faq/#metamargin">Meta-Margin:</a><span style="color: black"> %s</span></li>\n' % metamargin_str)

    outfile.write('\t<li class="rss"><a href="http://election.princeton.edu/feed/">RSS</a></li>\n')
    #outfile.write('\t<li style="float: center; clear: both; padding-top: 0px;"><a href="%s" style="text-decoration: underline">Probability of Democratic+Independent control: %s in an election today, %s on Election Day</a></li>\n' % (bottom_url, control_prob_str, november_pred_str))
    outfile.write('\t<li style="float: center; clear: both; padding-top: 0px; padding-left: 0px"><a href="%s">Election Day Probability of 50 or more Democratic+Independent seats:</a><span title="%s" style="color:black"> %s</span><span title="%s" style="color:black; margin-left: 40px">Meta-Margin: <a href="%s">%s</a></span></li>\n' % (bottom_url, november_pred_range, november_pred_str, november_mm_range, error_url, november_mm_str))

    outfile.close()

    ############################################################################

if __name__ == '__main__':
    try:
        infile = open(sys.argv[1], 'r')
    except:
        infile = open('Senate_estimates.csv', 'r')

    try:
        nov_infile = open(sys.argv[2], 'r')
    except:
        nov_infile = open('Senate_D_November_control_probability.csv', 'r')

    try:
        outfile = open(sys.argv[3], 'w')
    except:
        outfile = open('current_senate.html', 'w')


    main(infile, nov_infile, outfile)
