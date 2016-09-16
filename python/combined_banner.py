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
def format_prob(prob, percentage=True):
    if prob <= 0.9:
        rounded = int(round(prob * 100) * 1) # round to nearest 1% (20,5 for 5%)
        #rounded = int(round(prob * 100)) # NEW round to nearest 1% instead
        return '%s' % rounded if percentage else '.%s' % rounded
    elif prob <= 97.0:
        rounded = int(round(prob * 100)) # round to nearest 1%
        return "%s" % rounded if percentage else '.%s' % rounded
    else:
        rounded = int(round(prob * 1000)) /10.0 # round to nearest 0.1%
        return "%.1f" % rounded if percentage else '.%s' % int(rounded * 10)

def main(mm_infile, prob_infile, sen_infile, outfile):

    time_str = "%s %s, %s:%s" % (time.strftime("%B"), int(time.localtime()[2]),
            int(time.strftime("%I")), time.strftime("%M%p %Z"))

    # metamargin stuff
    values = mm_infile.read()[:-1].split(",")
    mm_infile.close()

    dem_ev = values[0]
    gop_ev = values[1]
    num_polls = values[11]
    ev_metamargin = float(values[12])

    # probability stuff
    values = prob_infile.read()[:-1].split(",")
    prob_infile.close()

    bayesian_win_prob = format_prob(float(values[0]))
    drift_win_prob = format_prob(float(values[1]))

    # Senate stuff
    values = csv.reader(sen_infile).next() # get the first (and only) row
    sen_infile.close()
    dem_seats = int(values[0])
    gop_seats = 100 - dem_seats
    sen_metamargin = float(values[10])
    sen_metamargin_str = ('D' if sen_metamargin > 0 else 'R') + ' %+.1f%%' % abs(sen_metamargin)
    sen_num_polls = int(values[7])

    # Senate probability stuff
    values = senpredict_infile.read()[:-1].split(",")
    senpredict_infile.close()

    Senate_bayesian_win_prob = format_prob(float(values[1])/100)

    # write output
    outfile.write('\t<li style="color: black">As of %s:</li>\n' % time_str)

    outfile.write(('\t<li><a href="/faq/">Snapshot (%s state polls)</a>:&nbsp;' +
            '<span style="color:blue">Clinton %s</span>,&nbsp;' +
            '<span style="color:red">Trump %s EV</span>&nbsp;&nbsp;&nbsp;&nbsp;' +
            '<a href="/faq/#metamargin">Meta-margin: ') % (num_polls, dem_ev, gop_ev))
    if ev_metamargin > 0:
        outfile.write('Clinton +%2.1f%%</a></li>\n' % ev_metamargin)
    elif ev_metamargin < 0:
        outfile.write('Trump +%2.1f%%</a></li>\n' % -ev_metamargin)
    else:
        outfile.write('Tied</a></li>\n')

    outfile.write('\t<li class="rss"><a href="http://election.princeton.edu/feed/">RSS</a></li>\n')

    outfile.write('\t<li style="clear: both; padding-top: 0px; /*padding-left: 60px*/; color: black; float: none">Clinton Nov. win probability: random drift %s%%, <a href="/2012/09/29/the-short-term-presidential-predictor/">Bayesian %s%%</a></li>\n' % (drift_win_prob, bayesian_win_prob))

    outfile.write('\t<li style="padding-top: 0px; color: black; float: none">Senate snapshot (%d polls):&nbsp;' % sen_num_polls)
    outfile.write('<a href="/todays-senate-seat-count-histogram/" style="color: blue">Dem+Ind:</a><span style="color: blue"> %s</span>,&nbsp;' % dem_seats)
    outfile.write('<a href="/todays-senate-seat-count-histogram/" style="color: red">GOP:</a><span style="color: red"> %s</span>,&nbsp;' % gop_seats)
    outfile.write('<a href="/faq/#metamargin">Meta-margin: %s</a>, ' % sen_metamargin_str)
    outfile.write('<a href="/2016/08/29/the-2016-senate-forecast/">Nov. control probability</a>: Dem. %s%%</li>\n' % Senate_bayesian_win_prob)

    outfile.close()

    ############################################################################

if __name__ == '__main__':
    try:
        mm_infile = open(sys.argv[1], 'r')
    except:
        mm_infile = open('EV_estimates.csv', 'r')

    try:
        prob_infile = open(sys.argv[2], 'r')
    except:
        prob_infile = open('EV_prediction_probs.csv', 'r')

    try:
        sen_infile = open(sys.argv[3], 'r')
    except:
        sen_infile = open('Senate_estimates.csv', 'r')

    try:
        senpredict_infile = open('foo','r')
    except:
        senpredict_infile = open('Senate_D_November_control_probability.csv', 'r')
        
    try:
        outfile = open(sys.argv[4], 'w')
    except:
        outfile = open('banner.html', 'w')


    main(mm_infile, prob_infile, sen_infile, outfile)
