import matplotlib.pyplot as plt
import numpy as np
import pyfits
from scipy.integrate import simps
from matplotlib.ticker import NullFormatter, MaxNLocator




def k(tdev,sig,gam,E,c0,c1,beta):			#king, tdev abweichung vom zentrum in rad
	X=tdev/np.sqrt((c0*(E/100)**beta)**2+c1**2)
	res=1/(2*pi*sig**2) *(1-1/gam) *(1+1/(2*gam)*(X/sig)**2)**(-gam)
	return res

def f(N,sigt,sigc):					#norm
	res=1/(1+N*(sigt/sigc)**2)
	return res

def p(tdev,sigc,gamc,sigt,gamt,N,E,c0,c1,beta):		#psf 	x=dRA, y=dDEC	umrechnung in rad noetig
	res=f(N,sigt,sigc)*k(tdev,sigc,gamc,E,c0,c1,beta)+(1-f(N,sigt,sigc))*k(tdev,sigt,gamt,E,c0,c1,beta)
	return res




# Define a function to make the ellipses
def ellipse(ra,rb,ang,x0,y0,Nb=100):
    xpos,ypos=x0,y0
    radm,radn=ra,rb
    an=ang
    co,si=np.cos(an),np.sin(an)
    the=np.linspace(0,2*np.pi,Nb)
    X=radm*np.cos(the)*co-si*radn*np.sin(the)+xpos
    Y=radm*np.cos(the)*si+co*radn*np.sin(the)+ypos
    return X,Y

def dangle(ra1,ra2,dec1,dec2): # each given in degrees
    dec1= 90.-dec1 # go from long to sphere
    dec2= 90.-dec2 # go from long to sphere

    sr1 = np.sin(ra1*d2r)
    cr1 = np.cos(ra1*d2r)

    sd1 = np.sin(dec1*d2r)
    cd1 = np.cos(dec1*d2r)

    sr2 = np.sin(ra2*d2r)
    cr2 = np.cos(ra2*d2r)

    sd2 = np.sin(dec2*d2r)
    cd2 = np.cos(dec2*d2r)

    resu = cr1*sd1*cr2*sd2 + sr1*sd1*sr2*sd2 + cd1*cd2
    resu[resu>1.0] = 1.0
    resu[resu<-1.0]= -1.0
    return(np.arccos(resu))

psf_fits=pyfits.open('./data/psf_P8R2_SOURCE_V6_PSF.fits')
dat=pyfits.open('./data/source_psf2_3.fits')	
#cut on evclass -> nur source (evclass=128)--- cut on evtype -> nur psf2/3 (evtype=16+32=48)

twopi=np.arctan(1.)*8.
pi=twopi/2.
d2r=pi/180.
r2d=180./pi

RAc=166.114			#position des zentrums
DECc=38.2088


cosTlist=np.cos(np.array(dat[1].data.field('THETA   '))*pi/180)	#liste der photonen neigungswinkel zum detektor (fuer thetabin) in cos(theta)
Elist=np.array(dat[1].data.field('ENERGY '))			#liste der photonenenergien in MeV
Ralist= np.array(dat[1].data.field('RA'))
Declist= np.array(dat[1].data.field('DEC'))
evtype = np.array(dat[1].data.field('EVENT_TYPE')[:,26])

drad = dangle(RAc*np.ones(Ralist.size),Ralist,DECc*np.ones(Declist.size),Declist)


# transformation:
Ralist = (Ralist-RAc)/np.cos(DECc*pi/180.)
Declist= Declist - DECc

# maximum cutout angle
maxa = 0.5

cosTlist = cosTlist[drad<(d2r*maxa)]
Elist  = Elist[drad<(d2r*maxa)]
Ralist = Ralist[drad<(d2r*maxa)]
Declist = Declist[drad<(d2r*maxa)]
drad = drad[drad<(d2r*maxa)]
evtype = evtype[drad<(d2r*maxa)]

print str(drad.size)+' Photons within '+str(maxa)+' degrees'

xlims=[min(Ralist),max(Ralist)]
ylims=[min(Declist),max(Declist)]

left,width=0.12,0.55
bottom,height=0.12,0.55
bottom_h=left_h=left+width+0.02

rect_sky = [left,bottom,width,height]
rect_histx = [left, bottom_h, width, 0.25] # dimensions of x-histogram
rect_histy = [left_h, bottom, 0.25, height] # dimensions of y-histogram

fig = plt.figure(1, figsize=(9.5,9))

axSky = plt.axes(rect_sky)
axHistx = plt.axes(rect_histx) # x histogram
axHisty = plt.axes(rect_histy) # y histogram

# remove the zero
nullfmt = NullFormatter()
axHistx.xaxis.set_major_formatter(nullfmt)
axHisty.yaxis.set_major_formatter(nullfmt)

xmin = min(xlims)
xmax = max(xlims)
ymin = min(ylims)
ymax = max(ylims)

# Define the number of bins
nxbins = 50
nybins = 50
nbins = 100

xbins = np.linspace(start = xmin, stop = xmax, num = nxbins)
ybins = np.linspace(start = ymin, stop = ymax, num = nybins)
xcenter = (xbins[0:-1]+xbins[1:])/2.0
ycenter = (ybins[0:-1]+ybins[1:])/2.0
aspectratio = 1.0*(xmax - 0)/(1.0*ymax - 0)


H, xedges,yedges = np.histogram2d(Declist,Ralist,bins=(ybins,xbins))
X = xcenter
Y = ycenter
Z = H

cax = (axSky.imshow(H, extent=[xmin,xmax,ymin,ymax],
           interpolation='nearest', origin='lower',aspect=aspectratio))

xcenter = np.mean(Ralist)
ycenter = np.mean(Declist)
rx = np.std(Ralist)
ry = np.std(Declist)

ang=0
X,Y=ellipse(rx,ry,ang,xcenter,ycenter)
axSky.plot(X,Y,"k:",ms=1,linewidth=2.0)
axSky.annotate('$1\\sigma$', xy=(X[15], Y[15]), xycoords='data',xytext=(10, 10),
                       textcoords='offset points', horizontalalignment='right',
                       verticalalignment='bottom',fontsize=25,color='white')

axSky.set_xlabel('Delta Ra',fontsize=25)
axSky.set_ylabel('Delte Dec',fontsize=25)

ticklabels = axSky.get_xticklabels()
for label in ticklabels:
    label.set_fontsize(18)
    label.set_family('serif')
 
ticklabels = axSky.get_yticklabels()
for label in ticklabels:
    label.set_fontsize(18)
    label.set_family('serif')

#Set up the plot limits
axSky.set_xlim(xlims)
axSky.set_ylim(ylims)
 
#Set up the histogram bins
xbins = np.arange(xmin, xmax, (xmax-xmin)/nbins)
ybins = np.arange(ymin, ymax, (ymax-ymin)/nbins)
 
#Plot the histograms
axHistx.hist(Ralist, bins=xbins, color = 'blue')
axHisty.hist(Declist, bins=ybins, orientation='horizontal', color = 'red')
 
#Set up the histogram limits
axHistx.set_xlim( min(Ralist), max(Ralist) )
axHisty.set_ylim( min(Declist), max(Declist) )
 
#Make the tickmarks pretty
ticklabels = axHistx.get_yticklabels()
for label in ticklabels:
    label.set_fontsize(12)
    label.set_family('serif')
 
#Make the tickmarks pretty
ticklabels = axHisty.get_xticklabels()
for label in ticklabels:
    label.set_fontsize(12)
    label.set_family('serif')
 
#Cool trick that changes the number of tickmarks for the histogram axes
axHisty.xaxis.set_major_locator(MaxNLocator(4))
axHistx.yaxis.set_major_locator(MaxNLocator(4))
plt.show()


# calculate the likelihood as a function of background-fraction
# assuming a point source at nominal position

ebin     = np.int_(np.floor((np.log10(Elist)/0.25-3)))
tbin     = np.int_(np.floor((cosTlist/0.1-2)))
psfclass = np.int_(np.ones(evtype.size)*2*np.logical_not(evtype)+ np.ones(evtype.size)*3*evtype)
psfind   = np.int_(psfclass*3+1)

sigc=map(lambda pind,tind,eind: psf_fits[pind].data.field('SCORE')[0][tind][eind] ,psfind,tbin,ebin)
gamc=map(lambda pind,tind,eind: psf_fits[pind].data.field('GCORE')[0][tind][eind], psfind,tbin,ebin)
sigt=map(lambda pind,tind,eind: psf_fits[pind].data.field('STAIL')[0][tind][eind], psfind,tbin,ebin)
gamt=map(lambda pind,tind,eind: psf_fits[pind].data.field('GTAIL')[0][tind][eind], psfind,tbin,ebin)
N   =map(lambda pind,tind,eind: psf_fits[pind].data.field('NTAIL')[0][tind][eind], psfind,tbin,ebin)
c0  =map(lambda pind: psf_fits[pind+1].data.field('PSFSCALE')[0][0], psfind)
c1  =map(lambda pind: psf_fits[pind+1].data.field('PSFSCALE')[0][1], psfind)
beta=map(lambda pind: psf_fits[pind+1].data.field('PSFSCALE')[0][2], psfind)

# corresponds to the same photon in Bjoern's test photon case 
# i=2
# print Elist[i],cosTlist[i],ebin[i],tbin[i],psfclass[i],psfind[i]
# print sigc[i],gamc[i],sigt[i],gamt[i],N[i],c0[i],c1[i],beta[i]





