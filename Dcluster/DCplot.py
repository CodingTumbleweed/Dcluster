import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np
from matplotlib.widgets import Button

try:
   input = raw_input
except NameError:
   pass

def plot1(rho, delta):
    f, axarr = plt.subplots(1,3)
    axarr[0].set_title('DECISION GRAPH')
    axarr[0].scatter(rho, delta, alpha=0.6,c='black')
    axarr[0].set_xlabel(r'$\rho$')
    axarr[0].set_ylabel(r'$\delta$')
    axarr[1].set_title('DECISION GRAPH 2')
    axarr[1].scatter(np.arange(len(rho))+1, -np.sort(-rho*delta), alpha=0.6,c='black')
    axarr[1].set_xlabel('Sorted Sample')
    axarr[1].set_ylabel(r'$\rho*\delta$')
    return(f,axarr)


def plot2(axarr,rho, delta,cmap,cl,icl,XY,NCLUST):
    axarr[0].scatter(rho, delta, alpha=1,c='black')
    axarr[1].scatter(np.arange(len(rho))+1, -np.sort(-rho*delta), alpha=1,c='black')
    for i in range(NCLUST):
        axarr[0].scatter(rho[icl[i]], delta[icl[i]], alpha=0.8, c=cmap[i])
        axarr[1].scatter(i+1, rho[icl[i]]*delta[icl[i]], alpha=0.8,c=cmap[i])
    axarr[2].set_title('2D multidimensional scaling')
    axarr[2].scatter( XY[:,0],  XY[:,1],alpha=0.8,c=cmap[list(cl)])
    axarr[2].set_xlabel('X')
    axarr[2].set_ylabel('Y')

def DCplot(dist, XY, ND, rho, delta,ordrho,dc,nneigh, rhomin,deltamin):
    f, axarr = plot1(rho, delta)
    def onclick(event):
        if event.inaxes == axes_save:
            btn_CallBack(event)
            return()
        global rhomin, deltamin
        if event.xdata != None and event.ydata != None:
            rhomin = event.xdata
            deltamin = event.ydata
            print('Cutoff: (min_rho, min_delta): (%.2f, %.2f)' %(rhomin,deltamin))
            NCLUST = 0
            cl = np.zeros(ND, dtype=int)-1
            # 1000 is the max number of clusters
            icl = np.zeros(1000, dtype=int)
            for i in range(ND):
                if rho[i]>rhomin and delta[i]>deltamin:
                    cl[i] = NCLUST
                    icl[NCLUST] = i
                    NCLUST = NCLUST+1

            print('NUMBER OF CLUSTERS: %i'%(NCLUST))
            print('Performing assignation')
            # assignation
            for i in range(ND):
                if cl[ordrho[i]]==-1:
                    cl[ordrho[i]] = cl[nneigh[ordrho[i]]]

            #halo
            # cluster id start from 1, not 0
            ## deep copy, not just reference
            halo = np.zeros(ND)
            halo[:] = cl

            if NCLUST>1:
                bord_rho = np.zeros(NCLUST)
                for i in range(ND-1):
                    for j in range((i+1),ND):
                        if cl[i]!=cl[j] and dist[i,j]<=dc:
                            rho_aver = (rho[i]+rho[j])/2
                            if rho_aver>bord_rho[cl[i]]:
                                bord_rho[cl[i]] = rho_aver
                            if rho_aver>bord_rho[cl[j]]:
                                bord_rho[cl[j]] = rho_aver
                for i in range(ND):
                    if rho[i]<bord_rho[cl[i]]:
                        halo[i] = -1

            for i in range(NCLUST):
                nc = 0
                nh = 0
                for j in range(ND):
                    if cl[j]==i:
                        nc = nc+1
                    if halo[j]==i:
                        nh = nh+1
                print('CLUSTER: %i CENTER: %i ELEMENTS: %i CORE: %i HALO: %i'%( i+1,icl[i]+1,nc,nh,nc-nh))
            # print , start from 1

            ## save CLUSTER_ASSIGNATION
            print('Generated file:CLUSTER_ASSIGNATION')
            print('column 1:element id')
            print('column 2:cluster assignation without halo control')
            print('column 3:cluster assignation with halo control')
            clusters = np.array([np.arange(ND)+1,cl+1,halo+1]).T
            np.savetxt('CLUSTER_ASSIGNATION_%.2f_%.2f_.txt'%(rhomin,deltamin),clusters,fmt='%d\t%d\t%d')
            print('Result are saved in file CLUSTER_ASSIGNATION_%.2f_%.2f_.txt'%(rhomin,deltamin))
            print('\n\nClick the mouse pointer at a cutoff position in figure 1')
            ################# plot the data points with cluster labels
            cmap = cm.rainbow(np.linspace(0, 1, NCLUST))
            if max(cl) != -1:
                plot2(axarr, rho, delta, cmap, cl, icl, XY, NCLUST)
                f.show()
            return()

    def btn_CallBack(event):
        f.canvas.mpl_disconnect(cid)
        print('Saving the figure in file CLUSTER_ASSIGNATION.png')
        figure = plt.gcf()  # get current figure
        figure.set_size_inches(24, 8)
        figure.savefig('CLUSTER_ASSIGNATION.png', dpi=300)

    axes_save = plt.axes([0.01, 0.9, 0.1, 0.075])
    btn_save = Button(axes_save, 'Save', color='lime')
    cid = f.canvas.mpl_connect('button_press_event', onclick)
    plt.show()