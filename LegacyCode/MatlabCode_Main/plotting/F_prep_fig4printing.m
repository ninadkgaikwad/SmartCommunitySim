function F_prep_fig4printing(figh)

%%
pos = get(figh,'paperposition');
%set the left and bottom to 0
set(figh,'paperposition',[0 0 5 2.5]); %(5 2.5) (pos(3) pos(4))
% the width and height are usally 8 in and 6 in
% while the papersize is 8.5 by 11
% For width, 0.5 in of buffer is ok, but 
% the 11 inch height of the paper means 5 inches of
% extra space: so get rid of both the extra width and height:
set(figh,'PaperSize',[ 5 2.5]); %(5 2.5) (pos(3) pos(4))





