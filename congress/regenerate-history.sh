#!/bin/bash

############################################################################
#
# This script is used to regenerate the history of Senate estimates
#
# Author: Andrew Ferguson <adferguson@alumni.princeton.edu>
# Modified by: Mark Tengi <markat@princeton.edu>
#
# Script written for election.princeton.edu run by Samuel S.-H. Wang under
# noncommercial-use-only license:
# You may use or modify this software, but only for noncommericial purposes.
# To seek a commercial-use license, contact sswang@princeton.edu
#
############################################################################

HISTORY=Senate_estimate_history.csv
POLLS=2014.Senate.polls.median.txt
NUM_PER_DAY=18

cd /web/matlab
mv $HISTORY $HISTORY.old # Make a backup
touch $HISTORY


mv $POLLS $POLLS.master
last_day=$((`wc -l $POLLS.master | awk '{print $1}'` / $NUM_PER_DAY))
day=1

while [ $day -le $last_day ]; do
    amount=$((day*$NUM_PER_DAY))
    echo "Day: $day, Amount: $amount"

    tail -$amount $POLLS.master > $POLLS

    matlab -nodisplay -r Senate_runner 2>&1 > /dev/null

    day=$((day+1))
done

# Since it's now the same as $POLLS
rm $POLLS.master
