#! /bin/bash

PYBIN=`which python`
function python() {
    TO_ADDR="sswang@princeton.edu"
    CC_ADDR="markat@princeton.edu"
    ERR_FILE="/tmp/err.txt"
    $PYBIN "$@" 2> >(tee $ERR_FILE)
    if [ "$?" != 0 ]; then
        { echo -e "Error message below:\n"; cat $ERR_FILE; } | mail -s "[URGENT] PEC: Error running $1" -c "$CC_ADDR" "$TO_ADDR"
    fi
    rm $ERR_FILE
}

# use this function as a replacement for python in all child scripts
export -f python
export PYBIN

# Run all of the necessary scripts
cd /web/current/

echo "!!!! Approval"
bash bin/approval.sh
echo "!!!! Congress"
bash bin/congress.sh
echo "!!!! EV"
bash bin/ev.sh

# Create the banner
cd /web/current/data/
python ../python/combined_banner.py
mv -f banner.html ../output/

python ../python/ev_jerseyvotes.py
python ../python/senate_jerseyvotes.py
python ../python/combined_jerseyvotes.py
mv -f *_jerseyvotes.html ../output/

# archive the produced CSVs and pictures
JULIAN=`date "+%j"`
cd /web/current/
tar -czf "data_archive/${JULIAN}.tgz" data/*
tar -czf "output_archive/${JULIAN}.tgz" output/*
