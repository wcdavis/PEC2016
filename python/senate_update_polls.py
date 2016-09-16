#!/usr/bin/python

############################################################################
#
# This Python script retrieves the CSV polling feeds from Huffington Post.
# The feeds are a structured representation of all of the polling data
# publicly accessible through their website. After retreiving the feeds, it
# produces an output file which contains summary statistics for the polling
# in each of the races we're watching (as specified in races.csv) as of each
# date since March 1. The summary statistics are described below under
# "Output Format".
#
# In other words, the first n (= number of races in races.csv) lines of
# output are summary statistics (s.s.) using all currently available polls
# (also known as "polls which ended before today"). The next n lines are the
# same s.s. recomputed, excluding polls ending today Then, the n lines are
# the s.s., omitting all polls ending today or yesterday, and so on, so that
# we have the history of these s.s. and can observe the effect of new polls.
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

import os, sys, urllib2, datetime, time, socket
from numpy import array, mean, median, sqrt, std
import csv

class RaceInfo(object):
    def __init__(self, line):
        self.state = line[0]
        self.dem = line[1]
        self.rep = line[2]
        self.assumption = line[3]
        self.url = "http://elections.huffingtonpost.com/pollster/2016-%s-senate-%s-vs-%s.csv" % (self.state, self.rep, self.dem).lower().replace(' ', '-')


states = {
        'AK': 'Alaska',
        'AL': 'Alabama',
        'AR': 'Arkansas',
        'AS': 'American Samoa',
        'AZ': 'Arizona',
        'CA': 'California',
        'CO': 'Colorado',
        'CT': 'Connecticut',
        'DC': 'District of Columbia',
        'DE': 'Delaware',
        'FL': 'Florida',
        'GA': 'Georgia',
        'GU': 'Guam',
        'HI': 'Hawaii',
        'IA': 'Iowa',
        'ID': 'Idaho',
        'IL': 'Illinois',
        'IN': 'Indiana',
        'KS': 'Kansas',
        'KY': 'Kentucky',
        'LA': 'Louisiana',
        'MA': 'Massachusetts',
        'MD': 'Maryland',
        'ME': 'Maine',
        'MI': 'Michigan',
        'MN': 'Minnesota',
        'MO': 'Missouri',
        'MP': 'Northern Mariana Islands',
        'MS': 'Mississippi',
        'MT': 'Montana',
        'NA': 'National',
        'NC': 'North Carolina',
        'ND': 'North Dakota',
        'NE': 'Nebraska',
        'NH': 'New Hampshire',
        'NJ': 'New Jersey',
        'NM': 'New Mexico',
        'NV': 'Nevada',
        'NY': 'New York',
        'OH': 'Ohio',
        'OK': 'Oklahoma',
        'OR': 'Oregon',
        'PA': 'Pennsylvania',
        'PR': 'Puerto Rico',
        'RI': 'Rhode Island',
        'SC': 'South Carolina',
        'SD': 'South Dakota',
        'TN': 'Tennessee',
        'TX': 'Texas',
        'UT': 'Utah',
        'VA': 'Virginia',
        'VI': 'Virgin Islands',
        'VT': 'Vermont',
        'WA': 'Washington',
        'WI': 'Wisconsin',
        'WV': 'West Virginia',
        'WY': 'Wyoming'
}
############################################################################
#
# Global configuration and variables
#
############################################################################

output_filename = "2016.Senate.polls.median.txt"
midtype = "median"
num_recent_polls_to_use = 3
archive_dir = "archive/senate/"

# Percentage to subtract from Dem-affiliated polls and add to Rep-affiliated ones
# Used to generate polls.median.Xcorrected.txt
bias_correction = 3
corrected_filename_parts = ("2016.Senate.polls.median.", "corrected.txt")

# Utility functions for getting the appropriate data from the CSV returned by HuffPo
# Can be used for sorting: y = sorted(x, key = start_date)
# For sorting by multiple keys: y = sorted(x, key = lambda z: (start_date(z), pollster(z)))
POLLSTER, START_DATE, END_DATE, ENTRY_DATE, NUM_OBS, POP_TYPE, MODE, DEM, REP, DIFF,\
        POLLSTER_URL, SOURCE_URL = tuple(range(12))
pollster =      lambda x: x[POLLSTER]
start_date =    lambda x: x[START_DATE]
end_date =      lambda x: x[END_DATE]
entry_date =    lambda x: x[ENTRY_DATE]
num_obs =       lambda x: x[NUM_OBS]
pop_type =      lambda x: x[POP_TYPE]
mode =          lambda x: x[MODE]
dem =           lambda x: x[DEM]
rep =           lambda x: x[REP]
diff =          lambda x: x[DIFF]
pollster_url =  lambda x: x[POLLSTER_URL]
source_url =    lambda x: x[SOURCE_URL]

margin =        lambda x: x[0]
start_date =    lambda x: x[1]
end_date =      lambda x: x[2]
mid_date =      lambda x: x[3]
pop =           lambda x: x[4]
poll_org =      lambda x: x[5]

# for reading race info from the csv file
# expected format: state, dem, rep, assumption
races_info_file = 'senate_data.csv'
header_row = True
DEM_NAME, REP_NAME, ASSUMPTION, URL = tuple(range(4)) # TODO use RaceInfo objects instead

races_info = {}
# races_info is a dictionary containing the information in the file specified
# by races_info_file. Each key is a state abbreviation and each value is a list,
# with the form [DEM_NAME, REP_NAME, ASSUMPTION, URL]


############################################################################
#
# Main
#
############################################################################

def main():
    global midtype
    global output_filename
    global races
    global races_info

    races_info = read_races_info(races_info_file, header_row)

    # get the latest polls and store the info in the races dict
    socket.setdefaulttimeout(5)
    races = fetch_latest_polls()

    process_polls(races)

############################################################################
#
# Returns the median and std. error
#
############################################################################

# The std. error is given by:
#         std. deviation / sqrt(num of polls)
#
# We robustly estimate the std. deviation from the median absolute
# deviation (MAD) using the standard formula:
#        std. deviation =  MAD / invcdf(0.75)
#
# The MAD is defined as median( abs[samples - median(samples)] )
# invcdf(0.75) is approximately 0.6745

def get_statistics(margins):

    num = margins.size
    assert num >= 3

    if midtype == "median":
        median_margin = median(margins)
        mad = median(abs(margins - median_margin))
        sem_est = mad/0.6745/sqrt(num)

        #Sometimes SEM is 0. Sam want this to be replaced by SD/sqrt(n)
        if sem_est == 0:
            sem_est = std(margins) / sqrt(num)

        return (median_margin, sem_est)

    else:
        assert midtype == "mean"

        mean_margin = mean(margins)
        sem = std(margins) / sqrt(num)

        return (mean_margin, sem)

# Special case for when only two polls are available

def get_two_statistics(margins):

    assert margins.size == 2

    mean_margin = mean(margins)
    sem = max(std(margins) / sqrt(margins.size), 3)

    return (mean_margin, sem)

# Special case where there's only one poll, and it might be the pseudopoll
def get_one_statistics(polls, pseudo, correct_bias):
    assert len(polls) == 1

    poll = polls[0]
    if pseudo: # Use hard-coded SEM of 0.05
            return (poll[0], 0.05)
    else: # currently this will never run because we add a pseudopoll if there's only 1 real poll
          # It should work though
        if poll[-1] == 'D' and (correct_bias == 'D' or correct_bias == 'B'):
            margin = poll[0] - bias_correction
        elif poll[-1] == 'R' and (correct_bias == 'R' or correct_bias == 'B'):
            margin = poll[0] + bias_correction
        else:
            margin = poll[0]

        return (margin, sqrt(1.0/poll[4]))


# Get the array of margins, allowing for a bias correction
def get_margins_array(polls, correct_bias):
    if correct_bias == 'D': #for each poll: get the margin, and correct for bias if it's from a Democratic pollster
        margins = [p[0] - bias_correction if p[-1] == 'D' else p[0] for p in polls]
    elif correct_bias == 'R':
        margins = [p[0] + bias_correction if p[-1] == 'R' else p[0] for p in polls]
    elif correct_bias == 'B':
        margins = [p[0] - bias_correction if p[-1] == 'D' else (p[0] + bias_correction if p[-1] == 'R' else p[0]) for p in polls]
    else:
        margins = [p[0] for p in polls]

    return array(margins)


############################################################################
#
# Functions to write the statistics which Sam's MATLAB scripts will use as
# inputs. There is one line of statistics for each state and D.C., for
# each date from today back to May 22
#
############################################################################

# Output Format -- 5 numbers per state
#    - number of polls used for average
#    - middle date of oldest poll used (January 1= 1)
#    - average margin where margin>0 is Obama ahead of Romney
#    - estimated SEM of margin
#    - analysisdate (written by the 'process_polls' method)

# Remember, the format of the tuple for each list:
# (margin, start date, end date, mid date, pop, polling organization, affil)

def write_statistics(pfile, polls, pseudo, correct_bias):
    # Number of polls available on this date for this state
    num = len(polls)

    #rnum is the number of real polls (excluding pseudo)
    rnum = num - 1 if pseudo else num

    polls.sort(key=mid_date, reverse=True)

    # Get the mid date of the oldest poll
    date = int(polls[-1][3].strftime('%j'))

    def w(num, date, stats):
        pfile.write('%2d  ' % num)
        pfile.write('%3s  ' % date)
        pfile.write('% 5.1f  %.4f  ' % stats)

    if num == 0:
        assert False
    elif num == 1:
        w(rnum, date, get_one_statistics(polls, pseudo, correct_bias))
    elif num == 2:
        margins = get_margins_array(polls, correct_bias)
        w(rnum, date, get_two_statistics(margins))
    else:
        margins = get_margins_array(polls, correct_bias)
        w(rnum, date, get_statistics(margins))

def process_polls(races):
    pfile = open(output_filename, 'w')

    # These files show the outcome if a bias is assigned to:
    # D: just Democratic pollsters
    # R: just Republican pollsters
    # B: both parties
    dfile = open('D'.join(corrected_filename_parts), 'w')
    rfile = open('R'.join(corrected_filename_parts), 'w')
    bfile = open('B'.join(corrected_filename_parts), 'w')

    for day in campaign_season():
        date = int(day.strftime('%j'))
        print 'processing polls for day %d' % date

        # Make a file to which we'll log the polls used in calculating today's numbers, and write the header
        dayfile = open(os.path.join(archive_dir, str(date)) + '.csv', 'w')
        dayfile_writer = csv.writer(dayfile)
        dayfile_writer.writerow(['state', 'margin', 'start_date', 'end_date', 'mid_date', 'pop', 'polling_org', 'affiliation'])

        for state_num, state in one_indexed_enumerate(sorted(races.keys())):

            cleaned = clean_polls(races[state], day)

            need_pseudo = add_pseudopoll(state, cleaned)

            for f, correct_bias in [(pfile, None), (dfile, 'D'), (rfile, 'R'), (bfile, 'B')]:
                write_statistics(f, cleaned, need_pseudo, correct_bias)

                # Write the date and the index of the state
                f.write('%3d  %2d\n' % (date, state_num))

            for poll in cleaned:
                dayfile_writer.writerow([state] + list(poll))

        dayfile.close()

    pfile.close()
    dfile.close()
    rfile.close()
    bfile.close()

# Add a pseudopoll to the list of polls, if necessary. Return True if we needed to do so
def add_pseudopoll(state, polls):
    if len(polls) >= num_recent_polls_to_use:
        return False
    
    # get the specified assumption to use from races_info
    assumption = float(races_info[state][ASSUMPTION])
    date = datetime.date(2016, 1, 1)

    # (margin, start date, end date, mid date, pop, polling organization, affil)
    polls.append((assumption, date, date, date, 1, 'FAKE: Assumption', None))
    return True

# Clean up the polls, following Sam's rules
def clean_polls(polls, day):

    # -1. Make sure there's something to clean
    if not polls:
        return []

    # 0. Sort the polls by ending date
    polls.sort(key = end_date, reverse = True)

    # 1. Drop all polls ending after "today"
    polls = filter(lambda x: x[2] < day, polls)

    # 2. Only use the latest poll from each organization
    pollsters = []
    def seen(pollster):
        if pollster in pollsters:
            return True
        else:
            pollsters.append(pollster)
            return False

    polls = [poll for poll in polls if not seen(poll_org(poll))]

    # If we don't need to eliminate any more polls, return
    if len(polls) < num_recent_polls_to_use:

        return polls

    # 3. Find third oldest mid date of a poll, and include any from this date or newer
    polls.sort(key=mid_date, reverse=True)
    third_oldest_date = mid_date(polls[num_recent_polls_to_use - 1])

    # 4. Find N weeks ago, where N is a function of "today"
    if day < datetime.date(2016, 8, 1): # Before August 1
        n = datetime.timedelta(7 * 6, 0, 0) # 6 weeks
    elif day < datetime.date(2016, 9, 1):   # Month of August
        n = datetime.timedelta(7 * 4, 0, 0) # 4 weeks
    elif day < datetime.date(2016, 10, 1):  # September
        #n = datetime.timedelta(7 * 2, 0, 0) # 2 weeks
	n = datetime.timedelta(28 - (day.day - 1) / 2, 0, 0) # Ease from 28 days to 14 over the course of the month
    else:                                   # October onwards
        n = datetime.timedelta(7 * 2, 0, 0) # now also 2 weeks
    n_weeks_ago = day - n

    # 5. Return all polls with a median date of (#3) or newer, or an ending date of (#4) or newer
    return filter(lambda x: x[3] >= third_oldest_date or x[2] >= n_weeks_ago, polls)

############################################################################
#
# Functions to fetch the latest polls from the Huffington Post
#
############################################################################


def url_fetcher(url):
    tries = 0
    while True:
        try:
            f = urllib2.urlopen(url)
            return f
        except urllib2.HTTPError as e:
            if e.code == 404:
                print "404 for %s" % url
                return None
        except urllib2.URLError:
            if tries < 3:
                tries += 1
                time.sleep(1)
            else:
                print "FAIL on %s (tried three times)" % url
                sys.stdout.flush()
                raise

# Get the latest polls from Huffington Post, and save them to the archive directory
def fetch_latest_polls():
    races = {}
    for state in races_info:
        races[state] = []
    # races is a dictionary with an entry for each state. Each entry
    # is a list of tuples. Each tuple represents one poll and is of the form:
    # (margin, start date, end date, mid date, population, polling organization, affiliation)

    for state, info in races_info.iteritems():
        print 'Getting polls for: %s' % state
        url = info[URL]
        if not url: # no url given in race_info_file
            print 'nothing to fetch for %s. We\'ll use the given assumption' % state
            continue

        # Try to deal with timeouts
        tries = 0
        while True:
            try:
                page = url_fetcher(url)
                break
            except socket.timeout:
                if tries < 3:
                    tries += 1
                    time.sleep(1)
                else:
                    print 'Kept timing out on: %s. Aborting' % state
                    exit()

        # if we can't fetch the page, just continue
        if not page:
            continue

        reader = csv.reader(page, delimiter=',')

        # Get the first row, containing the names
        header = reader.next()
        mapping = {} # {column number: column name}
        for i in range(len(header)):
            mapping[header[i].strip()] = i # Updated 08/21/16 to account for 'Undecided ' (note space) in IN CSV
        header[mapping["Undecided"]] = 'Difference' # This was 'Undecided' in the csv from HuffPo

        # Determine whether the candidates are in the correct order (Dem, then Rep)
        dem_name = info[DEM_NAME].split(" ")[0]
        rep_name = info[REP_NAME].split(" ")[0]
        #reverse = None

        # Check to see if we have an exact match
        #if dem(header) == dem_name:
        #    reverse = False
        #elif dem(header) == rep_name:
        #    reverse = True

        # Check to see if the name we have is a partial match (part of a hyphenated name)
        #if reverse == None:
        #    if dem(header).startswith(dem_name) or dem(header).endswith(dem_name):
        #        reverse = False
        #    elif dem(header).startswith(rep_name) or dem(header).endswith(rep_name):
        #        reverse = True
        #    elif rep(header).startswith(dem_name) or rep(header).endswith(dem_name):
        #        reverse = True
        #    elif rep(header).startswith(rep_name) or rep(header).endswith(rep_name):
        #        reverse = False

        # Something is very wrong with the names. We can't handle this situation
        #if reverse == None:
        #    print 'Could not handle names. Looking for:'
        #    print 'Dem: %s' % dem_name
        #    print 'Rep: %s' % rep_name
        #    print 'Got instead:'
        #    print 'In Dem spot: %s' % dem(header)
        #    print 'In Rep spot: %s' % rep(header)
        #    exit(1)

        rows = []
        for row in reader:
            #if reverse: # the Dem and Rep are flipped in the returned page
            #    row[DEM], row[REP] = row[REP], row[DEM]

            start_date = strpdate(row[mapping["Start Date"]])
            end_date = strpdate(row[mapping["End Date"]])
            mid_date = start_date + ((end_date - start_date) / 2)

            # Determine the pollster's apolitical affiliation
            affil = None
            pster = row[mapping["Pollster"]]
            if pster.find('(D') != -1:
                affil = 'D'
            elif pster.find('(R') != -1:
                affil = 'R'

            # Trim off any parenthesizes info (such as the party and/or organization
            # for whom the poll was taken), as well as any partner organizations
            pster = pster.split('(')[0].split('/')[0].strip()

            # Replace the Undecided vote with the difference between Dem and Rep
            row[mapping["Undecided"]] = float(row[mapping[dem_name]]) - float(row[mapping[rep_name]])

            # Store the info in the form:
            # (margin, start_date, end_date, mid_date, pop, poll_org, affil)
            races[state].append((row[mapping["Undecided"]], start_date, end_date, mid_date, row[mapping["Number of Observations"]], pster, affil))
            rows.append(row)

        # Write all of the data to a file in the archive dir
        with open(os.path.join(archive_dir, state) + '.csv', 'w') as f:
            writer = csv.writer(f, delimiter=',')
            writer.writerow(header)
            writer.writerows(rows)
            print 'Wrote %d polls to %s.csv' % (len(rows), state)

    return races

############################################################################
#
# Functions to process poll data from Huffington Post. Adds tuples of
# the form (margin, start_date, end_date, mid_date, pop, poll_org) to the
# races dictionary. The margin is defined as: Dem - GOP
#
############################################################################

def read_races_info(csvfile = races_info_file, header_row = True):
    with open(csvfile, 'rb') as f:
        reader = csv.reader(f, delimiter=',', quotechar='"')
        races_info = {}

        # Discard of the first row if necessary
        if header_row:
            reader.next()

        for row in reader:
            #if not row[1] or not row[2]: # We only want races with two candidates given
            #    print "Didn't find two candidates for %s. Ignoring state" % row[0]
            #    continue
            if row[4]:
                url = row[4] if row[4].endswith(".csv") else row[4] + ".csv"
            else:
		url = ("http://elections.huffingtonpost.com/pollster/2016-%s-senate-%s-vs-%s.csv" % (states[row[0]], row[2], row[1])).lower().replace(' ', '-')

            races_info[row[0]] = row[1:4] + [url]

    return races_info

############################################################################
#
# Utility functions and data
#
############################################################################

# Parses a date_string into a datetime.date. Included here to support
# Python 2.4, which lacks datetime.datetime.strpdate()

def strpdate(date_string, format="%Y-%m-%d"):
    return datetime.date(*(time.strptime(date_string, format)[0:3]))


# Generates all of the dates in the general election campaign season,
# starting from today and working back to March 1

def campaign_season():
    day = datetime.date.today()
    start = datetime.date(2016, 3, 1)

    while day >= start:
        yield day
        day = day - datetime.timedelta(1, 0, 0)

# Take an iterable and enumerate it, but use 1-indexing
# This makes MATLAB happy
def one_indexed_enumerate(d):
    for num, item in enumerate(d):
        yield (num + 1, item)


if __name__ == '__main__':
    #if len(sys.argv < 2):
    #    print("usage: update_polls_senate.py outfilename")
    try:
        main()
    except KeyboardInterrupt:
        pass
