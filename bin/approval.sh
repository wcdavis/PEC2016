#!/bin/bash

# Get/process data relating to the Presidential approval rating
# Expects to be run from /web/XXXX/ as `sh bin/approval.sh`

DIR=`pwd -P`
export PYTHONDIR=$DIR/python
export MATLABDIR=$DIR/matlab
export BINDIR=$DIR/bin
export OUTDIR=$DIR/output
export DATADIR=$DIR/data
export PYTHONPATH=$PYTHONDIR:$PYTHONPATH

export APPROVAL_FILE=approval_polls.csv
export CULLED_APPROVAL_FILE=culled_polls.csv
export APPROVAL_MATLAB_FILE=obama_approval_matlab.csv # specified in Obama_timeseries.m
export POLLSTERS_FILE=pollsters.p
export APPROVAL_HISTORY_FILE=Obama_approval_history.csv
export APPROVAL_HISTORY_GRAPH=Obama_generic_history.jpg
export APPROVAL_URL=http://elections.huffingtonpost.com/pollster/obama-job-approval.csv
export APPROVAL_BANNER=approval_banner.html

#XXX list of output files

cd $DATADIR

wget $APPROVAL_URL -O $APPROVAL_FILE
python $PYTHONDIR/cull_partisan_approvals.py $APPROVAL_FILE $CULLED_APPROVAL_FILE
python $PYTHONDIR/convert_huffpost_csv.py $CULLED_APPROVAL_FILE $APPROVAL_MATLAB_FILE $POLLSTERS_FILE
mv -f $APPROVAL_MATLAB_FILE $MATLABDIR
cd $MATLABDIR
sh $BINDIR/Xrun.sh "matlab -r Obama_runner"

mv -f $APPROVAL_HISTORY_FILE $DATADIR
mv -f $APPROVAL_HISTORY_GRAPH $OUTDIR

cd $DATADIR
python $PYTHONDIR/approval_banner.py
mv -f $APPROVAL_BANNER $OUTDIR
