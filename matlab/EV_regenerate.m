for analysisdate=143:(floor(now) - datenum(2016,1,0)) % Julian dates are 1-indexed
    metacalc=1;
    EV_estimator
    EVhistfilename=['oldhistograms/EV_histogram_' num2str(analysisdate,'%i') '.jpg']
    copyfile('EV_histogram_today.jpg',EVhistfilename);
end
