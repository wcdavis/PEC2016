#!/bin/sh

############################################################################
#
# This script is run several times per day by the Unix cron daemon to
# update the site. It first uses the Python update_polls.py script to
# prepare the summary statistics which are used by the MATLAB scripts it
# calls next. Then, it updates the automatically generated text and graphics
# which display the calculations using additional Python scripts.
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

# House stuff

wget http://elections.huffingtonpost.com/pollster/2016-national-house-race.csv
python convert_huffpost_csv.py 2016-national-house-race.csv house_race_matlab.csv pollsters.p


POLLS=2016.Senate.polls.median.txt 

./update_polls.py

# If this has already run today, trim off the last line
HISTORY=Senate_estimate_history.csv
if cat $HISTORY | grep -e ^`date +%j`
then
mv $HISTORY SEH.tmp
head -n -1 SEH.tmp > $HISTORY
rm -f SEH.tmp
fi

# Use Xvfb to appease MATLAB -- graphics won't render correctly without
# an X display
echo 'Starting Xvfb'
XVFB_DISPLAY=99
Xvfb :$XVFB_DISPLAY -screen 0 1280x1024x24 &
XVFB_PID=$!
export DISPLAY=:$XVFB_DISPLAY
echo 'Running MATLAB'
matlab -r Senate_runner

matlab -r Obama_House_runner
echo "Killing Xvfb with PID $XVFB_PID"
kill $XVFB_PID

echo 'Running final Python stuff'
./current_senate.py
./jerseyvotes.py

./stateprobs.py

#chmod a+r autotext/*
#chmod a+r autographics/*

