#!/bin/sh

############################################################################
#
# This script runs nightly.sh in a sandboxed environment, allowing the user
# to test modifications to any of the python or MATLAB scripts.
#
# Author: Mark Tengi <markat@princeton.edu>
#
# Script written for election.princeton.edu run by Samuel S.-H. Wang under
# noncommercial-use-only license:
# You may use or modify this software, but only for noncommericial purposes.
# To seek a commercial-use license, contact sswang@princeton.edu
#
############################################################################

HISTORY=Senate_estimate_history.csv
POLLS=2014.Senate.polls.median.txt 

# A (mostly) non-destructive way to test out new things. Some things will be
# overwritten (namely the python/archive/ directory), but it shouldn't do too
# much damage. Look in the output_test directory to see what your changes
# produced.


cd /web/

echo 'Backing everything up'
mv output output.temp
mkdir output

# Copy these so that the site will still work while this is running
mkdir autotext.temp
mkdir autographics.temp
cp -fr autotext/* autotext.temp/
cp -fr autographics/* autographics.temp/

cd bin/

echo 'Running nightly.sh'
# Run everything, essentially sandboxed
./nightly.sh

cd ..

echo 'Putting everything back'
rm -rf output_test
mv -f output output_test # This is the interesting place to look
mv -f output.temp output
rm -rf autotext
rm -rf autographics
mv -f autotext.temp autotext
mv -f autographics.temp autographics
cp -f output/$POLLS matlab/
cp -f output/$HISTORY matlab/


