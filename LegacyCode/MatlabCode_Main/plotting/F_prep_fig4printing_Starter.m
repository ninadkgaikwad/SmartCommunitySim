savefigs = 1;
if savefigs
    F_prep_fig4printing(gcf);
    print(gcf,'-dpdf','..\..\figures\abcde.pdf');
end