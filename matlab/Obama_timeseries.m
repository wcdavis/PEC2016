%LIBGL_DEBUG='verbose'
pdata=csvread('obama_approval_matlab.csv');

clear foo
foo(:,1)=(pdata(:,2)+pdata(:,3))/2-datenum('31-dec-2014'); %midpoint dates
foo(:,2)=pdata(:,3)-datenum('31-dec-2014'); %ebd dates
foo(:,3)=pdata(:,6)-pdata(:,7); %margins
foo(:,4)=pdata(:,1); %pollster ID numbers
[foo2,inds]=sort(foo(:,1),1,'descend'); % going to sort by midpoint date

middates=foo(inds,1);
enddates=foo(inds,2);
margins=foo(inds,3);
pollsters=foo(inds,4);

tod=today-datenum('31-dec-2014'); % Julian date this year
Nback=21; %days back to look

% for a given date
dstart=tod-366; dfinish=tod; d=dstart:dfinish;

for id=1:length(d)
    %   first, find polls meeting date criterion
    iNback=intersect(find(enddates>=d(id)-Nback),find(enddates<=d(id)));
    %   then clean these up for pollster-ID
    [c,ia,ic]=unique(pollsters(iNback),'first');
    iNback=iNback(ia);
    %
    %   second, find last 3 polls from different pollsters
    iback3=min(find(middates<=d(id)));
    iback3=iback3:min(iback3+19,length(middates)); % last 20 (if it requires more, blech)
    [c,ia,ic]=unique(pollsters(iback3),'first');
    iback3=iback3(ia); %   take uniques
    iback3=iback3(1:min(3,length(iback3))); % last 3 or less
    %
    %   union of these two groups
    iback=union(iNback,iback3);
    %
    %   then calculate descriptive statistics
    pmedian(id)=median(margins(iback));
    psem(id)=mad(margins(iback),1)/sqrt(length(iback))/0.6745;
end

close
trimmed=pmedian(end-365+1:end);
phandle=plot(d(length(d):-6:6),pmedian(length(d):-6:6),'-k','LineWidth',2)
hold on
%axis([dstart dfinish min(pmedian)-5 max(pmedian)+5])
axis([tod-365 tod+30 min(trimmed)-2 max(trimmed)+3])
plot([tod-365 tod+30],[0 0],'-r')
%plot(enddates,margins,'.r')
grid on
[max(d) mean(pmedian(find(d>=1))) std(pmedian(find(d>=1)))]

% omedian=pmedian;oSEM=psem;od=d;

hmedian=pmedian;hSEM=psem;hd=d;

firsts=datenum(0,[1:48],1);
set(gca,'XTick',firsts,'FontSize',12)
datetick('x', 'mmm', 'keeplimits', 'keepticks');
ylabel('Obama approval minus disapproval (%)','FontSize',14)
text(tod-365+6,min(trimmed)-1,'election.princeton.edu','FontSize',12)
set(gcf, 'InvertHardCopy', 'off');
title('Obama net job approval, current','FontSize',14)

%csvwrite('Obama_approval_history.csv',[d pmedian psem])
csvwrite('Obama_approval_history.csv',[d; pmedian; psem])
%set(gcf,'PaperPositionMode','auto')
%print -djpeg Obama_generic_history.jpg
screen2jpeg(['Obama_generic_history.jpg'])
%close
