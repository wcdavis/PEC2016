#/bin/sh

cd /web/python
wget http://elections.huffingtonpost.com/pollster/obama-job-approval.csv
wget http://elections.huffingtonpost.com/pollster/2014-national-house-race.csv
python convert_huffpost_csv.py obama-job-approval.csv obama_approval_matlab.csv pollsters.p
python convert_huffpost_csv.py 2014-national-house-race.csv house_race_matlab.csv pollsters.p
mv obama-job-approval.csv archive/
mv 2014-national-house-race.csv archive/
