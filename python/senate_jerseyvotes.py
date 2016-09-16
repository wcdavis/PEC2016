#!/usr/bin/env python

############################################################################
#
# This script produces an HTML table which displays the relative influence
# voters in different swing states have over the outcome of the election.
# The influence statistic is normalized so that NJ voters, living in a
# non-swing state have power 1.0, hence the term "jerseyvotes." The statistic
# is calculated by the MATLAB script Senate_jerseyvotes.m
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

from decimal import Decimal
from senate_update_polls import read_races_info, DEM_NAME, REP_NAME, URL
import csv

explanation_url = "http://election.princeton.edu/2012/10/14/jerseyvotes/"

jerseyvotes = []

# Get info on the races (candidate names, URL) from races.csv
races_info = read_races_info()

def display_state(jvdisplay, stateinfo):
    state, margin, power = stateinfo[1:]
    data_url = races_info[state][URL][:-4] # Strip off the '.csv' at the end of the URL
    dem_name = races_info[state][DEM_NAME]
    rep_name = races_info[state][REP_NAME]

    # Bold states with power >= 1
    bold, endbold = ('<b>', '</b>') if abs(power) > 1 else ('','')

    jvdisplay.write("<tr>\n")
    jvdisplay.write("\t<td>%s%s%s</td>" % (bold, state, endbold))

    fmtstring = '<td>%s<a href="%s" style="color: %s;">%s +%s%%</a>%s</td>'
    if state == 'MT':
        data_url = 'http://www.realclearpolitics.com/epolls/2014/senate/mt/montana_senate_daines_vs_curtis-5190.html'
    if margin > 0:
        if dem_name == 'Orman': # Special case for independent
            jvdisplay.write(fmtstring % (bold, 'http://elections.huffingtonpost.com/pollster/2014-kansas-senate-roberts-vs-orman-vs-taylor', 'green', dem_name, margin, endbold))
        else:
            jvdisplay.write(fmtstring % (bold, data_url, 'blue', dem_name, margin, endbold))
    elif margin < 0:
        jvdisplay.write(fmtstring % (bold, data_url, 'red', rep_name, -margin, endbold))
    else:
        jvdisplay.write('<td>%s<a href="%s" style="color: black;">Tied</a>%s</td>' % (bold, data_url, endbold))
    
    jvdisplay.write("<td>%s%#.1f%s</td>\n" % (bold, power, endbold))
    jvdisplay.write("</tr>\n")

# The jerseyvotes.csv file has the following format:
# state number, state abbreviation, margin, voter power (most powerful = 100)

with open("Senate_jerseyvotes.csv") as f:
    reader = csv.reader(f)
    for line in reader:
        line[2] = float(line[2])
        line[3] = float(line[3])
        jerseyvotes.append(line)

# Output the HTML table displaying the jerseyvotes ranking. It will be
# included into the blog sidebar by a WordPress widget.

jvdisplay = open("Senate_jerseyvotes.html", "w")

jvdisplay.write('<table id="jerseyvotes" width="100%" style="text-align: center;">\n')
jvdisplay.write("<tr>\n")
jvdisplay.write('\t<th>State</th><th>Margin</th><th><a href="%s">Power</a></th>\n' % explanation_url)
jvdisplay.write("</tr>\n")

# Get rid of the states with JV = 0
filtered = [jv for jv in jerseyvotes if jv[3] > 0]

for stateinfo in filtered:
    display_state(jvdisplay, stateinfo)

jvdisplay.write("</table>\n")
jvdisplay.close()
