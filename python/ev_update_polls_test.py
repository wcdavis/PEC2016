#!/usr/bin/python

############################################################################
#
# This Python script retrieves the XML polling feeds from Huffington Post
# The feeds are a structured representation of all of the polling data
# publicly accessible through their website. After retreiving the feeds, it
# produces an output file which contains summary statistics for the polling
# in each state (and D.C.), as of each date since May 22. The summary
# statistics are described below under "Output Format".
#
# In other words, the first 51 lines of output are summary statistics (s.s.)
# using all currently available polls (also known as "polls which ended
# before today"). The next 51 lines of output are the same s.s. recomputed,
# but omitting any polls which ended before yesterday. Then, the 51 lines
# of s.s., omitting the polls which ended before two days ago, and so on,
# so that we have the history of these s.s. and can observe the effect of
# new polls.
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
#    Jul 10, 2012 -- Updated for new HuffPo XML format
#    Jul  8, 2012 -- Export CSV files for exploratory analysis
#    Jul  7, 2012 -- Initial port from 2008 version
#    
############################################################################

import os, sys, urllib2, datetime, time, xml.dom.minidom, socket
from numpy import *

############################################################################
#
# Global configuration and variables
#
############################################################################

output_filename = "2016.EV.polls.median_test.txt"
midtype = "median"
num_recent_polls_to_use = 3
huffpo_base_url = ""
huffpo_childNodes_per_page = 21 # 10 polls per page, plus space childNode on either side
archive_dir = "archive/ev/"

state_polls = {}
# state_polls is a dictionary with each an entry for each state. Each entry
# is a list of tuples. Each tuple represents one poll and is of the form:
# (margin, start date, end date, mid date, population, polling organization)

prev_outcome = {}
# prev_outcome is a dictionary like state_polls with a single tuple recording
# the outcome from the previous election for states which have had sparse
# polling, if any, during the current campaign

poll_ids = []
max_filenum = 0

# Files for exploratory analysis
state_filename = "2016_StatePolls_test.csv"
state_file = None
national_filename = "2016_NationalPolls_test.csv"
national_file = None

us_state_abbrev = {
    'alabama': 'AL',
    'alaska': 'AK',
    'arizona': 'AZ',
    'arkansas': 'AR',
    'california': 'CA',
    'colorado': 'CO',
    'connecticut': 'CT',
    'delaware': 'DE',
    'florida': 'FL',
    'georgia': 'GA',
    'hawaii': 'HI',
    'idaho': 'ID',
    'illinois': 'IL',
    'indiana': 'IN',
    'iowa': 'IA',
    'kansas': 'KS',
    'kentucky': 'KY',
    'louisiana': 'LA',
    'maine': 'ME',
    'maryland': 'MD',
    'massachusetts': 'MA',
    'michigan': 'MI',
    'minnesota': 'MN',
    'mississippi': 'MS',
    'missouri': 'MO',
    'montana': 'MT',
    'nebraska': 'NE',
    'nevada': 'NV',
    'new-hampshire': 'NH',
    'new-jersey': 'NJ',
    'new-mexico': 'NM',
    'new-york': 'NY',
    'north-carolina': 'NC',
    'north-dakota': 'ND',
    'ohio': 'OH',
    'oklahoma': 'OK',
    'oregon': 'OR',
    'pennsylvania': 'PA',
    'rhode-island': 'RI',
    'south-carolina': 'SC',
    'south-dakota': 'SD',
    'tennessee': 'TN',
    'texas': 'TX',
    'utah': 'UT',
    'vermont': 'VT',
    'virginia': 'VA',
    'washington': 'WA',
    'west-virginia': 'WV',
    'wisconsin': 'WI',
    'wyoming': 'WY',
    'united-states': 'US', # not sure if this is right
}

############################################################################
#
# Main
#
############################################################################

def main():
    global max_filenum
    global midtype
    global output_filename
    global huffpo_base_url
    global state_file, national_file

    try:
        if sys.argv[1] == "--mean":
            midtype = "mean"
            output_filename = "polls.mean.txt"
    except:
        pass

    for state in state_names:
        state_polls[state] = []

    state_file = init_analysis_file(state_filename)
    national_file = init_analysis_file(national_filename)
    store_prev_outcome()
    
    # load base url
    huffpo_config = open(".huffpo.url")
    huffpo_base_url = huffpo_config.readline()[:-1]
    huffpo_config.close()

    # process archive of polls
    #for fname in os.listdir(archive_dir):
    #    n = int(fname.split(".")[0])
    #    if n > max_filenum:
    #        max_filenum = n
    #    parse_pollfile(archive_dir + fname)

    # get the latest polls
    socket.setdefaulttimeout(5)
    fetch_latest_polls()

    process_polls()

    state_file.close()
    national_file.close()


def init_analysis_file(filename):
    outfile = open(filename, "w+")

    outfile.write("State,pollster,pop,vtype,method,begmm,begdd,begyy,")
    outfile.write("endmm,enddd,endyy,trump,clinton,other,undecided,")
    outfile.write("Begdate,Enddate,Middate\n")

    return outfile


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

def get_statistics(set):
    [margins, sdates, edates, mdates, pop, poll_orgs] = zip(*set)
    set = array(margins)

    num = set.size
    assert num >= 3

    if midtype == "median":
        median_margin = median(set)
        mad = median(abs(set - median_margin))
        sem_est = mad/0.6745/sqrt(num)

        return (median_margin, sem_est)

    else:
        assert midtype == "mean"

        mean_margin = mean(set)
        sem = std(set) / sqrt(num)

        return (mean_margin, sem)

# Special case for when only two polls are available

def get_two_statistics(set):
    [margins, sdates, edates, mdates, pop, poll_args] = zip(*set)
    set = array(margins)

    assert set.size == 2

    mean_margin = mean(set)
    sem = max(std(set) / sqrt(set.size), 3)

    return (mean_margin, sem)


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
#    - average margin where margin>0 is Clinton ahead of Trump
#    - estimated SEM of margin
#    - analysisdate (written by the 'process_polls' method)

# Remember, the format of the tuple for each list:
# (margin, start date, end date, mid date, pop, polling organization)

def write_statistics(pfile, polls, nopolls):
    # Number of polls available on this date for this state
    num = len(polls)

    if num == 0:
        assert False
    elif num == 1:
        pfile.write("%s " % (0 if nopolls else num)) # if there were no real polls, write 0 in first column
        pfile.write("%s " % int(polls[0][3].strftime("%j")))
        pfile.write("%s " % polls[0][0])
        pfile.write("%s " % sqrt(1.0/polls[0][4]))
    elif num == 2:
        pfile.write("%s " % num)
        pfile.write("%s " % int(polls[1][3].strftime("%j")))
        pfile.write("%s %s " % get_two_statistics(polls))
    else:
        # We want to use only the three most recent polls, as defined by the
        # midpoint date, and allowing for ties
        polls.sort(key=lambda x: x[3], reverse=True)
        third_date = polls[num_recent_polls_to_use - 1][3]
        last_three = filter(lambda x: x[3] >= third_date, polls)

        # Or, if this gives more polls, use the polls from the 7 days prior
        # to the most recent poll.
        polls.sort(key=lambda x: x[3], reverse=True)
        most_recent_date = polls[0][3]
        seven_days_prior = most_recent_date - datetime.timedelta(7, 0, 0)
        last_seven_days = filter(lambda x: x[3] >= seven_days_prior, polls)

        if (len(last_seven_days) > len(last_three)):
            working_subset = last_seven_days
        else:
            working_subset = last_three

        pfile.write("%s " % len(working_subset))
        pfile.write("%s " % int(working_subset[-1][3].strftime("%j")))
        pfile.write("%s %s " % get_statistics(working_subset))


def drop_overlapping_polls(polls):
    if len(polls) <= 1:
        return polls

    cleaned_polls = []

    # sort by: pollster, start date (old to new), end date (old to new)
    by_pollster = sorted(polls, key=lambda x: (x[5], x[1], x[2]))

    prev_pollster = by_pollster[0][5]
    prev_start    = by_pollster[0][1]
    prev_end      = by_pollster[0][2]
    prev_poll     = by_pollster[0]
    cleaned_polls.append(by_pollster[0])

    for poll in by_pollster[1:]:
        if prev_pollster != poll[5]:
            prev_pollster = poll[5]
        else:
            if prev_end > poll[1]:
                cleaned_polls.pop()

        prev_start    = poll[1]
        prev_end      = poll[2]
        prev_poll     = poll
        cleaned_polls.append(poll)

    # write_statistics expects polls to be sorted from newest to oldest
    # by mid-date
    cleaned_polls.sort(key=lambda x: x[3], reverse=True)
    return cleaned_polls

def process_polls():
    pfile = open(output_filename, "w")

    # Make sure the polls are sorted with most recent first
    for state in state_polls.keys():
        polls = state_polls[state]
        polls.sort(key=lambda x: x[2], reverse=True)

    # Write the 51 lines of output statistics for each day, from now
    # back to May 22
    for day in campaign_season():
        statenum = 1
        for state in sorted(state_names, key=lambda x: state_names[x]):
            polls = state_polls[state]

            # Remember, the format of the tuple for each list:
            # (margin, start date, end date, mid date, pop, polling org)
            polls_ended_before_day = filter(lambda x: x[2] < day, polls)

            #  reject two polls by the same pollster if their
            # [startdate,enddate] intervals overlap (i.e. if older
            # enddate>=newer startdate).
            cleaned_polls = drop_overlapping_polls(polls_ended_before_day)

            nopolls = False
            if len(cleaned_polls) == 0:
                cleaned_polls = [ prev_outcome[state] ]
                nopolls = True

            write_statistics(pfile, cleaned_polls, nopolls)
            pfile.write("%s %d\n" % (int(day.strftime("%j")), statenum))
            statenum += 1

    pfile.close()

############################################################################
#
# Functions to fetch the latest polls from the Huffington Post
#
############################################################################


def url_fetcher(page_num, state):
    tries = 0
    while True:
        url = 'http://elections.huffingtonpost.com/pollster/api/polls.xml?question=16-%s-Pres-GE%%20TrumpvClinton&page=%s'
        try:
            f = urllib2.urlopen(url % (state, str(page_num)))
            return f
        except urllib2.URLError:
            if tries < 3:
                tries += 1
                time.sleep(2)
            else:
                print "FAIL on page %d (tried three times)" % page_num
                sys.stdout.flush()
                raise


def fetch_latest_polls():
    global max_filenum

    polls = 0
    for state in us_state_abbrev.values():
        page_num = 0
        stop = False
        while (not stop):
            page_num += 1
            print "Fetching page %s for %s" % (str(page_num), state)
            page = url_fetcher(page_num, state)

            (xmldoc, stop, n) = parse_pollfile(page, state)
            polls += n
            xmldoc.childNodes[0].normalize()

            #if len(xmldoc.childNodes[0].childNodes) > 1:
            #    max_filenum += 1
            #    f = open(archive_dir + str(max_filenum) + ".xml", 'w')
            #    s=xmldoc.toxml(encoding="utf-8")
            #    f.write(s)
            #    f.close()
            #    print "Wrote %d polls to %s" % (0.5 * (len(xmldoc.childNodes[0].childNodes) - 1), str(max_filenum))

            if not stop:
                time.sleep(1)

    #print "got %d polls" % polls


############################################################################
#
# Functions to process poll data from Huffington Post. Adds tuples of
# the form (margin, start_date, end_date, mid_date, pop, poll_org) to the
# state_polls dictionary. The margin is defined as: Dem - GOP
#
############################################################################


def parse_pollfile(filename, state):
    (xmldoc, stop) = unique_polls(filename)
    n = process_pollfile(xmldoc, state)
    return (xmldoc, stop, n)


def unique_polls(filename):
    xmldoc = xml.dom.minidom.parse(filename)
    
    pi_nodes = xmldoc.getElementsByTagName("id")

    if len(pi_nodes) == 0:
        return (xmldoc, True)
    
    for pi_node in pi_nodes:
        poll_id = int(pi_node.childNodes[0].nodeValue)

        if poll_id in poll_ids:
            poll_node = pi_node.parentNode
            polls = poll_node.parentNode
            polls.removeChild(poll_node)
        else:
            poll_ids.append(poll_id)
    
    return (xmldoc, False)


def get_opt_subelem(elem, name, default):
    tmp = elem.getElementsByTagName(name)
    if len(tmp) > 0 and tmp[0].hasChildNodes():
        return tmp[0].childNodes[0].nodeValue
    return default


def subpop_parse(subpop):
    values = {"Clinton":"", "Trump":"", "Other":"", "Undecided":""}

    vtype = get_opt_subelem(subpop, "name", "")
    pop = int(get_opt_subelem(subpop, "observations", "0"))

    responses = subpop.getElementsByTagName("response")

    for r in responses:
        candidate = r.getElementsByTagName("choice")[0].childNodes[0].nodeValue
        value = r.getElementsByTagName("value")[0].childNodes[0].nodeValue
        values[candidate] = value
        
    assert(values["Clinton"] != "")
    assert(values["Trump"] != "")

    return (vtype, pop, values)


def process_subpop(poll_org, method, state, start_date, end_date, subpop):
    global state_file, national_file

    (vtype, pop, values) = subpop_parse(subpop)

    mid_date = start_date + ((end_date - start_date) / 2)
    margin = int(values["Clinton"]) - int(values["Trump"]) 
    f = None

    if state != "US" and pop != 0: # XXX does 0 check effectively fix issue with no reported pop?
        state_polls[state].append((margin, start_date, end_date,
                                   mid_date, pop, poll_org))
        f = state_file
    else:
        f = national_file

    d = (start_date.month, start_date.day,start_date.year,
         end_date.month, end_date.day, end_date.year,
         mid_date.month, mid_date.day, mid_date.year)
    f.write("%s,\"%s\",%d,\"%s\",\"%s\"," % (state, poll_org, pop, vtype, method))
    f.write("%d,%d,%d,%d,%d,%d," % d[:6])
    f.write("%s,%s,%s,%s," % (values["Trump"], values["Clinton"],
        values["Other"], values["Undecided"]))
    f.write("%s/%s/%s,%s/%s/%s,%s/%s/%s\n" % d)


def process_pollfile(xmldoc, state):
    def x():
        topics = xmldoc.getElementsByTagName("topic")
        
        presTopics = filter(lambda x: x.hasChildNodes() and 
                x.childNodes[0].nodeValue=="2016-president", topics)

        questions = map(lambda x: x.parentNode, presTopics)

        # further filter the questions to find only those asking trump vs. clinton
        charts = xmldoc.getElementsByTagName("chart")
        
        TCcharts = filter(lambda x: x.hasChildNodes() and 
                x.childNodes[0].nodeValue.endswith("trump-vs-clinton"), charts)

        TCquestions = map(lambda x: x.parentNode, TCcharts)
        questions = set(questions).intersection(set(TCquestions))

    codes = xmldoc.getElementsByTagName("code")
    presCodes = filter(lambda x: x.hasChildNodes() and x.childNodes[0].nodeValue.endswith("Pres-GE TrumpvClinton"), codes)
    questions = map(lambda x: x.parentNode, presCodes)

    for q in questions:
        try:
            poll = q.parentNode.parentNode
            poll_org = poll.getElementsByTagName("pollster")[0].childNodes[0].nodeValue
            method = get_opt_subelem(poll, "method", "")
            def x():
                try:
                    state = q.getElementsByTagName("state")[0].childNodes[0].nodeValue
                except IndexError:
                    chart = q.getElementsByTagName("chart")[0].childNodes[0].nodeValue
                    i = chart.index("-president")
                    statename = chart[5:i]
                    state = us_state_abbrev[statename]
            start_date = strpdate(poll.getElementsByTagName("start_date")[0].childNodes[0].nodeValue)
            end_date = strpdate(poll.getElementsByTagName("end_date")[0].childNodes[0].nodeValue)

            if start_date < datetime.date(2016, 1, 1):
                continue

            subpops = q.getElementsByTagName("subpopulation")

            if len(subpops) >= 2:
                for subpop in subpops:
                    vtype = get_opt_subelem(subpop, "name", "")
                    if vtype == "Likely Voter":
                        process_subpop(poll_org, method, state, start_date, end_date, subpop)
            else:
                for subpop in subpops:
                    process_subpop(poll_org, method, state, start_date, end_date, subpop)
            #print q.parentNode.parentNode.getElementsByTagName("id")[0].childNodes[0].nodeValue, state
        except:
            try:
                print "Problem processing poll #%s" % q.parentNode.parentNode.getElementsByTagName("id")[0].childNodes[0].nodeValue
                print q.parentNode.parentNode.toprettyxml()
            except:
                print "Very bad problem with below question. Ignoring:"
                print q.toprettyxml()
                raise

    return len(questions)


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
# starting from today and working back to May 22nd

def campaign_season():
    day = datetime.date.today()
    # start = datetime.date(2012, 5, 22)
    start = datetime.date(2016, 5, 22)

    while day >= start:
        yield day
        day = day - datetime.timedelta(1, 0, 0)


# Hard-code 2012 results for several states since there is no current
# polling data and political analysts do not disagree on the expected outcome.

def store_prev_outcome():
    prev_outcome["AL"] = (-22, datetime.date(2016,1,1),
        datetime.date(2016,1,1), datetime.date(2016,1,1), 1, "Election 2012")
    prev_outcome["AK"] = (-14, datetime.date(2016,1,1),
        datetime.date(2016,1,1), datetime.date(2016,1,1), 1, "Election 2012")
    prev_outcome["AR"] = (-24, datetime.date(2016,1,1),
        datetime.date(2016,1,1), datetime.date(2016,1,1), 1, "Election 2012")
    prev_outcome["CO"] = (5, datetime.date(2016,1,1),
        datetime.date(2016,1,1), datetime.date(2016,1,1), 1, "Election 2012")
    prev_outcome["CT"] = (17, datetime.date(2016,1,1),
        datetime.date(2016,1,1), datetime.date(2016,1,1), 1, "Election 2012")
    prev_outcome["DC"] = (83, datetime.date(2016,1,1),
        datetime.date(2016,1,1), datetime.date(2016,1,1), 1, "Election 2012")
    prev_outcome["DE"] = (19, datetime.date(2016,1,1),
        datetime.date(2016,1,1), datetime.date(2016,1,1), 1, "Election 2012")
    prev_outcome["HI"] = (43, datetime.date(2016,1,1),
        datetime.date(2016,1,1), datetime.date(2016,1,1), 1, "Election 2012")
    prev_outcome["ID"] = (-32, datetime.date(2016,1,1),
        datetime.date(2016,1,1), datetime.date(2016,1,1), 1, "Election 2012")
    prev_outcome["IL"] = (16, datetime.date(2016,1,1),
        datetime.date(2016,1,1), datetime.date(2016,1,1), 1, "Election 2012")
    prev_outcome["IN"] = (-7.5, datetime.date(2016,1,1),
        datetime.date(2016,1,1), datetime.date(2016,1,1), 1, "Election 2012")
    prev_outcome["KS"] = (-22, datetime.date(2016,1,1),
        datetime.date(2016,1,1), datetime.date(2016,1,1), 1, "Election 2012")
    prev_outcome["KY"] = (-23, datetime.date(2016,1,1),
        datetime.date(2016,1,1), datetime.date(2016,1,1), 1, "Election 2012")
    prev_outcome["LA"] = (-17, datetime.date(2016,1,1),
        datetime.date(2016,1,1), datetime.date(2016,1,1), 1, "Election 2012")
    prev_outcome["ME"] = (15, datetime.date(2016,1,1),
        datetime.date(2016,1,1), datetime.date(2016,1,1), 1, "Election 2012")
    prev_outcome["MA"] = (23, datetime.date(2016,1,1),
        datetime.date(2016,1,1), datetime.date(2016,1,1), 1, "Election 2012")
    prev_outcome["MS"] = (-3, datetime.date(2016,1,1),
        datetime.date(2016,1,1), datetime.date(2016,1,1), 1, "Election 2012")
    prev_outcome["MT"] = (-14, datetime.date(2016,1,1),
        datetime.date(2016,1,1), datetime.date(2016,1,1), 1, "Election 2012")
    prev_outcome["NE"] = (-22, datetime.date(2016,1,1),
        datetime.date(2016,1,1), datetime.date(2016,1,1), 1, "Election 2012")
    prev_outcome["NV"] = (7, datetime.date(2016,1,1),
        datetime.date(2016,1,1), datetime.date(2016,1,1), 1, "Election 2012")
    prev_outcome["NJ"] = (11, datetime.date(2016,1,1),
        datetime.date(2016,1,1), datetime.date(2016,1,1), 1, "Election 2012")
    prev_outcome["NM"] = (8, datetime.date(2016,1,1),
        datetime.date(2016,1,1), datetime.date(2016,1,1), 1, "Election 2012")
    prev_outcome["ND"] = (-20, datetime.date(2016,1,1),
        datetime.date(2016,1,1), datetime.date(2016,1,1), 1, "Election 2012")
    prev_outcome["OK"] = (-34, datetime.date(2016,1,1),
        datetime.date(2016,1,1), datetime.date(2016,1,1), 1, "Election 2012")
    prev_outcome["OR"] = (4.5, datetime.date(2016,1,1),
        datetime.date(2016,1,1), datetime.date(2016,1,1), 1, "Election 2012")
    prev_outcome["RI"] = (28, datetime.date(2016,1,1),
        datetime.date(2016,1,1), datetime.date(2016,1,1), 1, "Election 2012")
    prev_outcome["SC"] = (-10, datetime.date(2016,1,1),
        datetime.date(2016,1,1), datetime.date(2016,1,1), 1, "Election 2012")
    prev_outcome["SD"] = (-18, datetime.date(2016,1,1),
        datetime.date(2016,1,1), datetime.date(2016,1,1), 1, "Election 2012")
    prev_outcome["TN"] = (-20, datetime.date(2016,1,1),
        datetime.date(2016,1,1), datetime.date(2016,1,1), 1, "Election 2012")
    prev_outcome["TX"] = (-16, datetime.date(2016,1,1),
        datetime.date(2016,1,1), datetime.date(2016,1,1), 1, "Election 2012")
    prev_outcome["UT"] = (-5.5, datetime.date(2016,1,1),
        datetime.date(2016,1,1), datetime.date(2016,1,1), 1, "Election 2012")
    prev_outcome["VT"] = (36, datetime.date(2016,1,1),
        datetime.date(2016,1,1), datetime.date(2016,1,1), 1, "Election 2012")
    prev_outcome["WA"] = (15, datetime.date(2016,1,1),
        datetime.date(2016,1,1), datetime.date(2016,1,1), 1, "Election 2012")
    prev_outcome["WV"] = (-27, datetime.date(2016,1,1),
        datetime.date(2016,1,1), datetime.date(2016,1,1), 1, "Election 2012")
    prev_outcome["WY"] = (-41, datetime.date(2016,1,1),
        datetime.date(2016,1,1), datetime.date(2016,1,1), 1, "Election 2012")
    # put dummy data for every state. Remove loop once real data from 2012 is acquired
    # for state in state_names:
    #     prev_outcome[state] = (0, datetime.date(1900,1,1), datetime.date(1900,1,1), datetime.date(1900,1,1), 1, "BAD DATA")



state_names = {
    'AL': 'Alabama',
    'AK': 'Alaska',
    'AZ': 'Arizona',
    'AR': 'Arkansas',
    'CA': 'California',
    'CO': 'Colorado',
    'CT': 'Connecticut',
    'DC': 'D.C.',
    'DE': 'Delaware',
    'FL': 'Florida',
    'GA': 'Georgia',
    'HI': 'Hawaii',
    'ID': 'Idaho',
    'IL': 'Illinois',
    'IN': 'Indiana',
    'IA': 'Iowa',
    'KS': 'Kansas',
    'KY': 'Kentucky',
    'LA': 'Louisiana',
    'ME': 'Maine',
    'MD': 'Maryland',
    'MA': 'Massachusetts',
    'MI': 'Michigan',
    'MN': 'Minnesota',
    'MS': 'Mississippi',
    'MO': 'Missouri',
    'MT': 'Montana',
    'NE': 'Nebraska',
    'NV': 'Nevada',
    'NH': 'New Hampshire',
    'NJ': 'New Jersey',
    'NM': 'New Mexico',
    'NY': 'New York',
    'NC': 'North Carolina',
    'ND': 'North Dakota',
    'OH': 'Ohio',
    'OK': 'Oklahoma',
    'OR': 'Oregon',
    'PA': 'Pennsylvania',
    'RI': 'Rhode Island',
    'SC': 'South Carolina',
    'SD': 'South Dakota',
    'TN': 'Tennessee',
    'TX': 'Texas',
    'UT': 'Utah',
    'VT': 'Vermont',
    'VA': 'Virginia',
    'WA': 'Washington',
    'WV': 'West Virginia',
    'WI': 'Wisconsin',
    'WY': 'Wyoming',
    }

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
