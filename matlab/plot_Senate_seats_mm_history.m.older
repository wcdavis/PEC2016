%LIBGL_DEBUG='verbose'
Senate_history=load('Senate_estimate_history.csv');
d=Senate_history(:,1);
medians=Senate_history(:,2);
means=Senate_history(:,3);
pr=Senate_history(:,4)*100;
meanm=Senate_history(:,11);
mm=Senate_history(:,12);

vrange=[45 54];
f=92;
phandle=plot([60 315],[mean(vrange) mean(vrange)],'-r','LineWidth',1);
hold on
monthticks=datenum(0,4:12,1);
set(gca,'xtick',monthticks)
set(gca,'ytick',[vrange(1):vrange(2)])
set(gca,'XTickLabel',{'              Apr','              May','              Jun','              Jul','              Aug','              Sep','              Oct','         Nov'})
grid on
axis([f 315 vrange])
plot(d,means,'-k','LineWidth',1.5)
% monthstarts=[32 61 92 122 153 183 214 245 275 306];
% for ii=1:length(monthstarts)
%    plot([monthstarts(ii) monthstarts(ii)],vrange,'-k')
% end
ylabel('Democratic/Independent seats (%)','FontSize',14)
text(f+3,0.95*vrange(1)+0.05*vrange(2),'election.princeton.edu','FontSize',12)
set(gcf, 'InvertHardCopy', 'off');
title('Average Democratic-controlled Senate seats, 2014','FontSize',14)

%set(gcf, 'Renderer', 'OpenGL')
[fillhandle,msg]=jbfill(d',Senate_history(:,10)'+0.1,Senate_history(:,9)'-0.1,'k','g',1,0.1); % for confidence interval band
% see http://www.mathworks.com/matlabcentral/fileexchange/loadFile.do?objectId=13188&objectType=FILE

%set(gcf,'PaperPositionMode','auto')
print -djpeg Senate_seat_history.jpg
%saveas(gcf,'Senate_seat_history.jpg','jpg')
close

% Now do Meta-margin plot
vrange=[-3 3];
f=92;

phandle=plot([60 315],[mean(vrange) mean(vrange)],'-r','LineWidth',1);
hold on
set(gca,'xtick',monthticks)
set(gca,'ytick',[vrange(1):vrange(2)])
set(gca,'XTickLabel',{'              Apr','              May','              Jun','              Jul','              Aug','              Sep','              Oct','         Nov'})
set(gca,'YTickLabel',{'R+3%','+2%','+1%','0','+1%','+2%','D+3%'})
grid on
axis([f 315 vrange])
plot(d,mm,'-k','LineWidth',1.5)
ylabel('Meta-margin (%)','FontSize',14)
text(f+3,0.95*vrange(1)+0.05*vrange(2),'election.princeton.edu','FontSize',12)
set(gcf, 'InvertHardCopy', 'off');
title('Popular meta-lead for Senate control, 2014','FontSize',14)

%set(gcf,'PaperPositionMode','auto')
print -djpeg Senate_metamargin_history.jpg
