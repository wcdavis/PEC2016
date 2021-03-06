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

def main(infile, outfile):

    ## Estimated electoral votes and the current meta-margin

    reader = csv.reader(infile)
    reader.next()
    approval = float(reader.next()[-1]) # get the last value of the second row
    infile.close()

    time_str = time.strftime("%B %d, %Y")

    approval_str = ('APPROVE' if approval > 0 else 'DISAPPROVE' if approval < 0 else 'NEUTRAL') + ' %.1f%%' % abs(approval)

    ## Write the website header

    outfile.write('<span style="text-align:center"><a href="/obama-job-approval/">Obama net:</a>&nbsp;<strong style="color:%s">%s</strong></span>\n' % ('green' if approval > 0 else 'red' if approval < 0 else 'black', approval_str))

    outfile.close()

    ############################################################################

if __name__ == '__main__':
    try:
        infile = open(sys.argv[1], 'r')
    except:
        infile = open('Obama_approval_history.csv', 'r')

    try:
        outfile = open(sys.argv[3], 'w')
    except:
        outfile = open('approval_banner.html', 'w')


    main(infile, outfile)
