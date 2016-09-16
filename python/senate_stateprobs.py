#!/usr/bin/env python

############################################################################
#
# This script produces an HTML table which displays the single-state win
# probabilities of the races we're tracking.
#
# Author: Mark Tengi <markat@princeton.edu>
#
# Script written for election.princeton.edu run by Samuel S.-H. Wang under
# noncommercial-use-only license:
# You may use or modify this software, but only for noncommericial purposes.
# To seek a commercial-use license, contact sswang@princeton.edu
#
############################################################################

import csv
from senate_update_polls import read_races_info, DEM_NAME, REP_NAME, URL

def writeprobs(s, stateprobs):
    races_info = read_races_info()
    
    s.write('<head><style> #stateprobs th, #stateprobs td { border: 1px solid black;} </style></head>')
    s.write('<table id="stateprobs" style="text-align: center; font-family: sans-serif; font-size: initial; border-collapse: collapse; width: 100%">\n')
    s.write('<tr>\n')
    s.write('\t<th rowspan="2">State</th>\n')
    s.write('\t<th rowspan="2">Current Margin</th>\n')
    s.write('\t<th colspan="3">Dem Nov. Win Probability</th>\n')
    s.write('</tr>\n<tr>')
    s.write('\t<th>No bias</th>\n')
    s.write('\t<th>D+2% bias</th>\n')
    s.write('\t<th>R+2% bias</th>\n')
    s.write('</tr>\n')

    for nov,margin,d2,r2,state in sorted(stateprobs, key=lambda x: float(x[1]), reverse=True):
        margin_f = float(margin)
        tied = margin_f == 0
        dem_ahead = margin_f > 0
        margin = margin.replace('-','') # trim off a leading '-' if present
        color = 'blue' if dem_ahead else ('balck' if tied else 'red')
        if state == 'KS' and dem_ahead: #Orman
            color = 'green'
        candidate = races_info[state][DEM_NAME] if dem_ahead else races_info[state][REP_NAME]
        margin_str = ('%s +%s%%' % (candidate, margin)) if not tied else 'Tied'
        url = races_info[state][URL][:-4]
        #margin_str = (('D+' if dem_ahead else 'R+') + margin.replace('-', '') + '%') if margin_f != 0 else 'Tied'
        #s.write('<td style="color: %s">%s+%s</td>' % (("blue" if dem_ahead else "red"), ("D" if dem_ahead else "R"), margin.replace('-','')))

        s.write('<tr>\n')
        s.write('\t<td>%s</td>\n' % state)
        s.write('\t<td><a style="color: %s" href="%s">%s</a></td>\n' % (color, url, margin_str))
        s.write('\t<td>%s%%</td>\n' % nov)
        s.write('\t<td>%s%%</td>\n' % d2)
        s.write('\t<td>%s%%</td>\n' % r2)
        s.write('</tr>\n')

    s.write('</table>\n')


with open("Senate_stateprobs.html", "w") as s:
    stateprobs = []
    with open("Senate_stateprobs.csv", "r") as f:
        reader = csv.reader(f)
        for line in reader:
            stateprobs.append(line[1:]) # first column is today's win prob

    writeprobs(s, stateprobs)
