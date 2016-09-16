#!/bin/bash

# Collect and process polls for the Presidential election
# Expects to be run from /web/XXXX/ as `sh bin/ev.sh`

DIR=`pwd -P`
export PYTHONDIR=$DIR/python
export MATLABDIR=$DIR/matlab
export JAVADIR=$DIR/java
export BINDIR=$DIR/bin
export OUTDIR=$DIR/output
export DATADIR=$DIR/data
export PYTHONPATH=$PYTHONDIR:$PYTHONPATH

export EV_POLLS_FILE=2016.EV.polls.median.txt # from ev_update_polls.py
export EV_HISTORY_FILE=EV_estimate_history.csv

cd $DATADIR

python $PYTHONDIR/ev_update_polls.py

# If this has already run today, trim off the last line
if [ -e $EV_HISTORY_FILE ] && cat $EV_HISTORY_FILE | grep -e ^`date +%j`
then
mv $EV_HISTORY_FILE EH.tmp
head -n -1 EH.tmp > $EV_HISTORY_FILE
rm -f EH.tmp
fi

#cp -f $EV_HISTORY_FILE $EV_POLLS_FILE $MATLABDIR #TODO do this with symlinks in matlab dir
cd $MATLABDIR

sh $BINDIR/Xrun.sh "matlab -r EV_runner"

mv -f EV_histogram.csv EV_estimates.csv EV_prediction.csv EV_jerseyvotes.csv EV_stateprobs.csv EV_prediction_MM.csv EV_prediction_probs.csv 270towin_URL.txt Sen_histogram.csv Sen_estimates.csv $DATADIR
mv -f EV_histogram_today.jpg $OUTDIR

cd $DATADIR

# postprocess
python $PYTHONDIR/ev_histogram.py
python $PYTHONDIR/ev_history_plot.py
python $PYTHONDIR/ev_jerseyvotes.py
python $PYTHONDIR/ev_map.py
python $PYTHONDIR/ev_metamargin_history_plot.py

mv *.png *.html $OUTDIR

mv -f ev_map_runner.sh $BINDIR
cd $JAVADIR
sh $BINDIR/ev_map_runner.sh
mv *.png *.png-white $OUTDIR
