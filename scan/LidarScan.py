# -*- coding: utf-8 -*-
"""
Created on Thu Aug 20 08:21:04 2020

@author: boonping
"""

import os,re

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

import numpy as np
import math
from sklearn.cluster import DBSCAN
from scipy.spatial import ConvexHull,Delaunay
from scipy import ndimage
from scipy.misc import imsave
from scipy.misc import imread
from PIL import Image
from skimage.draw import line_aa


from tensorflow.keras.models import Model,load_model
from keras.preprocessing.image import save_img
from tensorflow.keras import backend

'''
model = load_model('map_network_classifier13.hdf5')
model.load_weights("map_network_weight13.hdf5")
'''
from skimage.util import view_as_windows as viewW

def fill_zero_regions(a, kernel_size=3):
    hk = kernel_size//2 # half_kernel_size    

    a4D = viewW(a, (kernel_size,kernel_size))
    sliced_a = a[hk:-hk,hk:-hk]
    zeros_mask = sliced_a==0
    zero_neighs = a4D[zeros_mask].reshape(-1,kernel_size**2)
    n = len(zero_neighs) # num_zeros

    scale = zero_neighs.max()+1
    zno = zero_neighs + scale*np.arange(n)[:,None] # zero_neighs_offsetted

    count = np.bincount(zno.ravel(), minlength=n*scale).reshape(n,-1)
    modevals = count[:,1:].argmax(1)+1
    sliced_a[zeros_mask] = modevals
    return a

slicesize=1024
display=1
#for kk in range(0,468,20):
for kk in range(0,10,1):
    #opening pose file
    inf0=open("scan%03i.pose" % kk,"r")
    pos0=inf0.readline().replace("\n","").replace(" ",",")
    pos0=np.array(eval("["+pos0+"]"))
    eu=inf0.readline().replace("\n","").replace(" ",",")
    print("913",eu)
    eu=np.array( eval("["+eu+"]")  )*math.pi/180
    inf0.close()

    #rotation matrix (processing .pose file)
    matz=[[ math.cos(eu[2]) , -1*math.sin(eu[2]) , 0 ],[ math.sin(eu[2]) ,  1*math.cos(eu[2]) , 0 ],[ 0 , 0, 1] ]
    maty=[[ math.cos(eu[1]) , 0, 1*math.sin(eu[1]) ],[ 0 , 1, 0],[ -1*math.sin(eu[1]) , 0, 1*math.cos(eu[1])] ]
    matx=[ [1,0,0],[ 0, math.cos(eu[0]) , -1*math.sin(eu[0]) ],[ 0, math.sin(eu[0]) ,  1*math.cos(eu[0]) ] ]
    matz=np.array(matz)
    maty=np.array(maty)
    matx=np.array(matx)

    mat=np.matmul(matz,maty)
    mat=np.matmul(mat,matx)

    #process scan file 
    inf=open("scan%03i.3d" % kk,"r")
    buf=[]
    buf2=[]
    pos=inf.readline().replace("\n","").replace(" ",",")
    pos=np.array(eval("["+pos+"]"))
    print("934",pos)

    poolmaxx=-100000
    poolminx=100000
    poolmaxy=-100000
    poolminy=100000
    scan1=np.array([])

    for line in inf.readlines():
        line=line.replace("\n","").replace(" ",",")
        #print(line)
        p=eval("["+line+"]")
        buf.append(eval("["+line+"]"))
        
        posi=np.transpose( np.array(eval("["+line+"]")) )
        #res=np.round( np.matmul(mat,posi) ).astype('int')
        res=np.round( np.matmul(mat,posi)+pos0 ).astype('int')
    
        if np.abs(res[2]-pos0[2])<250 and np.abs(res[0]-pos0[0])<250:
            #print("991",pos,res)
            continue
        if res[1]<-5: continue
        if res[1]<0: res[1]=0
        res[1]=255-res[1]
        if res[1]<64: res[1]=64
        #if res[1]<128: res[1]=128

        scan1=np.append(scan1,res)
        scan1=scan1.reshape(int(scan1.shape[0]/3),3)

        
        if scan1.shape[0]==0:
            scan1=np.append(scan1,res)
            scan1=scan1.reshape(int(scan1.shape[0]/3),3)
        elif res[1]>=245 and res[1]<251:
            if scan1[ (scan1[:,0]==res[0]) & (scan1[:,2]==res[2]) ].shape[0]>0:
                scan1[ (scan1[:,0]==res[0]) & (scan1[:,2]==res[2]) ][:,1]=res[1]
            else:
                scan1=np.append(scan1,res)
                #print(scan1,res,scan1.shape)
                scan1=scan1.reshape(int(scan1.shape[0]/3),3)
        elif res[1]>=251:
            tempa=scan1[ (scan1[:,0]==res[0]) & (scan1[:,2]==res[2]) ]
            if tempa.shape[0]>0:
                if np.max(tempa[:,1])>246 and np.max(tempa[:,1])<251 :
                    continue
                scan1[ (scan1[:,0]==res[0]) & (scan1[:,2]==res[2]) ][:,1]=res[1]
            else:
                scan1=np.append(scan1,res)
                #print(scan1,res,scan1.shape)
                scan1=scan1.reshape(int(scan1.shape[0]/3),3)
                
        elif scan1[ (scan1[:,0]==res[0]) & (scan1[:,2]==res[2]) ].shape[0]>0:
            if np.min(scan1[ (scan1[:,0]==res[0]) & (scan1[:,2]==res[2]) ][:,1])>=245:
                continue
            if res[1]>np.max( scan1[ (scan1[:,0]==res[0]) & (scan1[:,2]==res[2]) ][:,1] )  and np.min(scan1[ (scan1[:,0]==res[0]) & (scan1[:,2]==res[2]) ][:,1])>=64:
                scan1[ (scan1[:,0]==res[0]) & (scan1[:,2]==res[2]) ][:,1]=res[1]

        else:
            scan1=np.append(scan1,res)
            scan1=scan1.reshape(int(scan1.shape[0]/3),3)
        
            

        #interpolation
        if 0: #res[1]>245:
            if res[0]>pos0[0]+255:
                #print("type1")
                xx=np.arange(pos0[0], res[0],8)
                yy=np.interp(xx,np.array([pos0[0],res[0]]),np.array([pos0[2],res[2]])).astype('int')
                for poi in np.arange(1,xx.shape[0]-1,1):
                    res_extra=np.array([xx[poi],251,yy[poi]])
                    if scan1[(scan1[:,0]==xx[poi])&(scan1[:,2]==xx[poi])].shape[0]!=0:
                        scan1[(scan1[:,0]==xx[poi])&(scan1[:,2]==xx[poi])]=251
                    else:
                        scan1=np.append(scan1,res_extra)
                        scan1=scan1.reshape(int(scan1.shape[0]/3),3)
            elif res[0]<pos0[0]-255:
                #print("type2")
                xx=np.arange(res[0],pos[0],8)
                
                yy=np.interp(xx,np.array([res[0],pos0[0]]),np.array([res[2],pos0[2]])).astype('int')
                if 0: #res[2]<pos0[2]:
                    print("type2")
                    print(xx,yy,pos0[0],res[0])
                    
                #print(xx,yy,pos0[0],res[0])
                for poi in np.arange(1, xx.shape[0]-1,1):
                    res_extra=np.array([xx[poi],251,yy[poi]])
                    if scan1[(scan1[:,0]==xx[poi])&(scan1[:,2]==xx[poi])].shape[0]!=0:
                        scan1[(scan1[:,0]==xx[poi])&(scan1[:,2]==xx[poi])]=251
                    else:
                        scan1=np.append(scan1,res_extra)
                        scan1=scan1.reshape(int(scan1.shape[0]/3),3)
            elif res[2]>pos0[2]+255:
                #print("type3")
                if res[0]<pos0[0]:
                    xx=np.arange(res[0], pos0[0],8)
                    yy=np.interp(xx,np.array([res[0],pos0[0]]),np.array([res[2],pos0[2]])).astype('int')
                else:    
                    xx=np.arange(pos0[0], res[0],8)
                    yy=np.interp(xx,np.array([pos0[0],res[0]]),np.array([pos0[2],res[2]])).astype('int')
                for poi in np.arange(1,xx.shape[0]-1,1):
                    res_extra=np.array([xx[poi],251,yy[poi]])
                    if scan1[(scan1[:,0]==xx[poi])&(scan1[:,2]==xx[poi])].shape[0]!=0:
                        scan1[(scan1[:,0]==xx[poi])&(scan1[:,2]==xx[poi])]=251
                    else:
                        scan1=np.append(scan1,res_extra)
                        scan1=scan1.reshape(int(scan1.shape[0]/3),3)
            elif res[2]<pos0[2]-255:
                #print("type4")
                if res[0]<pos0[0]:
                    xx=np.arange(res[0], pos0[0],8)
                    yy=np.interp(xx,np.array([res[0],pos0[0]]),np.array([res[2],pos0[2]])).astype('int')
                else:    
                    xx=np.arange(pos0[0], res[0],8)
                    yy=np.interp(xx,np.array([pos0[0],res[0]]),np.array([pos0[2],res[2]])).astype('int')
                #print(xx,yy,res[1])
                for poi in np.arange(1,xx.shape[0]-1,1):
                    res_extra=np.array([xx[poi],251,yy[poi]])
                    if scan1[(scan1[:,0]==xx[poi])&(scan1[:,2]==xx[poi])].shape[0]!=0:
                        scan1[(scan1[:,0]==xx[poi])&(scan1[:,2]==xx[poi])]=251
                    else:
                        scan1=np.append(scan1,res_extra)
                        scan1=scan1.reshape(int(scan1.shape[0]/3),3)

    inf.close()
                        
        
    if scan1.shape[0]==0: continue
    #scan1=scan1.reshape(int(scan1.shape[0]/3),3)
    #print(scan1.shape)
    '''
    scan1= scan1[ (scan1[:,0]).argsort() ]
    scan1=scan1.astype('int')
    scan1=np.unique(scan1,axis=0)

    sca=np.copy(scan1)
    print(sca.shape)
    scaa=np.copy(scan1[:,0])
    scab=np.copy(scan1[:,2])
    scac=np.dstack([scaa,scab])
    scac=scac.reshape(scac.shape[1],scac.shape[2])
    scac=np.unique(scac,axis=0)
    
    
    print(scac.shape)
    print( (sca[(sca[:,0]==scac[:,0]) & (sca[:,2]==scac[:,1])]))
    raise
    '''

    scan1= scan1[ (scan1[:,0]).argsort() ]
    
    if scan1.shape[0]==0: continue
    print(scan1.shape)
    scan1=scan1.astype('int')
    
    scan1=np.unique(scan1,axis=0)
    print(scan1.shape)
    
    #raise
    if np.max(scan1[:,0])>poolmaxx: poolmaxx=np.max(scan1[:,0])
    
    if np.min(scan1[:,0])<poolminx: poolminx=np.min(scan1[:,0])
    
    if np.max(scan1[:,2])>poolmaxy: poolmaxy=np.max(scan1[:,2])
    
    if np.min(scan1[:,2])<poolminy: poolminy=np.min(scan1[:,2])


    xmin=np.min(scan1[:,0])
    xmax=np.max(scan1[:,0])
    ymin=np.min(scan1[:,2])
    ymax=np.max(scan1[:,2])
    zmin=np.min(scan1[:,1])
    zmax=np.max(scan1[:,1])
    print(xmax,xmin,ymax,ymin,zmin,zmax)
    #raise
    nx=np.ceil( (xmax)/slicesize )
    ny=np.ceil( (ymax)/slicesize )
    #print(nx,ny)
    startx=math.floor(xmin/slicesize)*slicesize
    starty=math.floor(ymin/slicesize)*slicesize
    endx=math.floor(xmax/slicesize)*slicesize
    endy=math.floor(ymax/slicesize)*slicesize
                        
    x=np.arange(slicesize)
    y=np.arange(slicesize)
    map1=np.zeros((endx+slicesize-startx,endy+slicesize-starty))


    pos1=np.copy(pos0)
    pos1[0]-=startx
    pos1[2]-=starty
    pos1=pos1.astype('int')
    map1[scan1[:,0]-startx,scan1[:,2]-starty]=scan1[:,1]
    print("done extract map1",map1.shape)

    map1c=np.copy(map1)
    map1c[map1c<64]=0
    map1c[map1c>245]=0
    map1b=np.copy(map1)
    map1b[map1b<246]=0
    

    mas=np.copy(map1)
    mas[mas<246]=0
    mas[mas>0]=1
    mas1=1-mas
    mas=mas*map1
    
    
    xx,yy=np.nonzero(map1c)
    #print(xx,yy)
    #print("933a",pos1,xx.shape[0])

    for i in range(xx.shape[0]):
        rr, cc, val = line_aa(xx[i], yy[i], pos1[0], pos1[2])
        dist=(((xx[i]-pos1[0])**2 )+((yy[i]-pos1[2])**2 ))**0.5
        dis=(((rr-xx[i])**2 )+((cc-yy[i])**2 ))**0.5
        val=map1c[xx[i],yy[i]]+((253-map1c[xx[i],yy[i]])*dis/dist)
        #val[val<64]=64
        val=val.astype('int')
        rr=rr[val==64]
        cc=cc[val==64]
        val=val[val==64]
        
        #print(rr,cc,val,map1c[xx[i],yy[i]])
        #raise
        map1[rr, cc] = 64
    
    for i in range(xx.shape[0]):
        rr, cc, val = line_aa(xx[i], yy[i], pos1[0], pos1[2])
        dist=(((xx[i]-pos1[0])**2 )+((yy[i]-pos1[2])**2 ))**0.5
        dis=(((rr-xx[i])**2 )+((cc-yy[i])**2 ))**0.5
        #val=map1c[xx[i],yy[i]]+((253-map1c[xx[i],yy[i]])*dis/dist)
        val=map1c[xx[i],yy[i]]+((253-map1c[xx[i],yy[i]])*dis/dist)
        #val[val<64]=64
        val=val.astype('int')
        rr=rr[val>244]
        cc=cc[val>244]
        val=val[val>244]
        #print(rr,cc,val,map1c[xx[i],yy[i]])
        #raise
        map1[rr, cc] = val
    
    xx,yy=np.nonzero(map1b)
    #print(xx,yy)
    #print(pos1)

    #print("934a",pos1,xx.shape[0])
    for i in range(xx.shape[0]):
        rr, cc, val = line_aa(xx[i], yy[i], pos1[0], pos1[2])
        dist=(((xx[i]-pos1[0])**2 )+((yy[i]-pos1[2])**2 ))**0.5
        dis=(((rr-xx[i])**2 )+((cc-yy[i])**2 ))**0.5
        val=map1b[xx[i],yy[i]]+((253-map1b[xx[i],yy[i]])*dis/dist)
        #val[val<64]=64
        val=val.astype('int')
        rr=rr[val>244]
        cc=cc[val>244]
        val=val[val>244]
        #if xx[i]<2048 and yy[i]<2048:
            #print(rr,cc,val,map1b[xx[i],yy[i]])
            #print("958a",xx[i],yy[i],rr,cc)
        #raise
        map1[rr, cc] = 253

    #map1=map1*mas1
    #map1=map1+mas


    #raise
    
    for ii in range(0, map1.shape[0], slicesize):
        for jj in range(0, map1.shape[1], slicesize):
            if ii<poolminx-startx or ii>=poolmaxx-startx+slicesize: continue
            if jj<poolminy-starty or jj>=poolmaxy-starty+slicesize: continue
            map2=map1[ii:ii+slicesize,jj:jj+slicesize]
        

            
            if map2[map2>0].shape[0]<5 and map2[map2>244].shape[0]==0: continue
            if os.path.exists("mapim%i_%i.png" %(ii+startx,jj+starty)):
                maptemp=imread( "mapim%i_%i.png" %(ii+startx,jj+starty) )
                map2[maptemp>map2]=maptemp[maptemp>map2]

            imsave("mapim%i_%i.png" %(ii+startx,jj+starty), map2)

            '''
            if os.path.exists("t%i_%i.csv" %(ii+startx,jj+starty)):
                with open("t%i_%i.csv" %(ii+startx,jj+starty), "r") as f1:
                    try:
                        samp=np.loadtxt(f1)
                    except:
                        os.remove( "t%i_%i.csv" %(ii+startx,jj+starty) )
                        pass

                if samp.shape[0]!=0:
                    print("926",startx+ii,starty+jj)
                    print(samp)
                    print(samp.shape)
                    samp=samp.astype('int')
                    samp[:,0]-=(ii+startx)
                    samp[:,2]-=(jj+starty)
                    map2[samp[:,0],samp[:,2]]=np.copy(samp[:,1])
                else:
                    os.remove( "t%i_%i.csv" %(ii+startx,jj+starty) )
            '''
            #map2=map1[ii:ii+slicesize,jj:jj+slicesize]
            '''
            reseter=open("t%i_%i.csv" %(ii+startx,jj+starty), "w+")
            reseter.close()
            '''
            #print(np.diff(map2).shape)
            a=np.abs(np.diff(map2))
            b=np.append(a,np.zeros((a.shape[0],1)),axis=1)
            c=np.append(np.zeros((a.shape[0],1)),a,axis=1)
            #map2[b>5]=246
            #map2[c>5]=246
            a=np.abs(np.diff(map2,axis=0))
            b=np.append(a,np.zeros((1,a.shape[1])),axis=0)
            c=np.append(np.zeros((1,a.shape[1])),a,axis=0)
            #map2[b>5]=246
            #map2[c>5]=246
            #map3=np.copy( ndimage.gaussian_filter(map2, sigma=2) )
            map3=map2
            mask=np.copy(map2)
            mask[mask>0]=1
            map3=map3*mask
            
            mask2=np.copy(map2)
            mask2[mask2<245]=0
            mask2[(mask2>244)]=1
            map2=map2*mask2

            mask3=np.copy(map2)
            mask3[mask3<245]=1
            mask3[(mask3>244)]=0
            map3=map3*mask3

            map2[map3>map2]=map3[map3>map2]
            map5=map2
            
            #map2=map2/255
            #print(map2)
            #raise
            
            #map2+=64
            #map2[map2>255]=255
            #map2/=256
            #map2=map2.reshape(map2.shape[0],map2.shape[1],1)
            '''
            res_model=model.predict(np.expand_dims(map2,axis=0))
            
            
            im=255*res_model[0][:,:,0] #.reshape(slicesize,slicesize,1)
            im[im<64]=0
            
            im[map5>im]=map5[map5>im]
            im=fill_zero_regions(im.astype('int'))
            imsave("res%i_%i.png" %(ii+startx,jj+starty), im)
            
            
            poins1,poins3=np.nonzero(im)
            poins2=np.copy(im[np.nonzero(im)])
            #print(poins1,poins2,poins3)
            #print(np.dstack([poins1+startx,poins2.astype('int'),poins3+starty]))
            res23=np.dstack([poins1+startx+ii,poins2.astype('int'),poins3+starty+jj])
            res23=res23.reshape(res23.shape[1],res23.shape[2])
            print("928a",res23.shape)
            '''
            '''
            if res23.shape[0]<1:
                if os.path.exists("t%i_%i.csv" %(ii+startx,jj+starty)): os.remove( "t%i_%i.csv" %(ii+startx,jj+starty) )
                continue
            '''
            '''
            print("928",ii+startx,jj+starty)
            print(np.min(res23[:,0]),np.max(res23[:,0]))
            print(np.min(res23[:,1]),np.max(res23[:,1]))
            '''
            '''
            with open('t%i_%i.csv' %(ii+startx,jj+starty),'w+') as opener:
                #np.savetxt(opener, res23, newline=" ",fmt="%d", delimiter=",")
                if res23.shape[0]!=0:
                    np.savetxt(opener, res23)
                #opener.write("\n")
            '''
            '''
            with open("t%i_%i.csv" %(ii+startx,jj+starty), "r") as f:
                samp=np.loadtxt(f)
            '''
            #print(samp)
            #print(samp.shape)
            
            #print(samp.reshape( int(samp.shape[0]/3),3 ))
            #print(samp.shape)
            #raise
            '''
            print("973",im[im<64].shape)
            print(im[im>251].shape)
            print(im[(im>64)&(im<251)].shape)
            '''

            
            #im=im*255
            #im[im>64]=
            #im=im/192*255
            #print(im[(im<65) &(im>0)])
            im2=np.zeros((slicesize,slicesize,3))
            im=map2
            imsave("res%i_%i.png" %(ii+startx,jj+starty), im)
            ima=np.copy(im)
            imb=np.copy(im)
            imc=np.copy(im)
            #print("929",ima[ima>65])
            ima[ima<245]=0
            #ima[ima>0]=255

            '''
            imb[imb<246]=0
            imb[imb>250]=0
            imb[imb>0]=255
            '''
            imb=np.zeros(im.shape)
            #imb[imb>0]=0
            #imb[imb<240]=0
            '''
            aa=np.copy(imb)
            ab=np.abs(np.diff(aa,axis=0))
            bb=np.append(ab,np.zeros((1,ab.shape[1])),axis=0)
            cc=np.append(np.zeros((1,ab.shape[1])),ab,axis=0)
            bb[aa==0]=0
            cc[aa==0]=0
            bb[aa==bb]=0
            cc[aa==cc]=0
            bb[aa<64]=0
            cc[aa<64]=0
            imb[bb>5]=246
            imb[cc>5]=246

            ac=np.abs(np.diff(aa))
            bb=np.append(ac,np.zeros((ac.shape[0],1)),axis=1)
            cc=np.append(np.zeros((ac.shape[0],1)),ac,axis=1)
            bb[aa==0]=0
            cc[aa==0]=0
            bb[aa==bb]=0
            cc[aa==cc]=0
            bb[aa<64]=0
            cc[aa<64]=0
            imb[bb>5]=246
            imb[cc>5]=246
            '''
            
            '''
            a=np.abs(np.diff(imb))
            b=np.append(a,np.zeros((a.shape[0],1)),axis=1)
            c=np.append(np.zeros((a.shape[0],1)),a,axis=1)
            #map2[b>5]=246
            #map2[c>5]=246
            aa=np.copy(imb)
            a=np.abs(np.diff(aa,axis=0))
            b=np.append(a,np.zeros((1,a.shape[1])),axis=0)
            c=np.append(np.zeros((1,a.shape[1])),a,axis=0)
            imb[(b>5) & (aa!=b) & (aa>=245)]=246
            imb[(c>5) & (aa!=c) & (aa>=245)]=246
            ima[(b>5) & (aa!=b) & (aa>=245)]=0
            ima[(c>5) & (aa!=c) & (aa>=245)]=0
            imc[(b>5) & (aa!=b) & (aa>=245)]=0
            imc[(c>5) & (aa!=c) & (aa>=245)]=0
            '''
            #print("927",imb[imb>0].shape)
            
            imc[(imc<64)]=0
            imc[(imc>244)]=0
            imc[imc>0]=255-imc[imc>0]
            #print(imc[imc>0].shape)
            '''
            ima[ima==0]=64
            imb[imb==0]=64
            imc[imc==0]=64
            '''
            
            im2[:,:,0]=ima
            im2[:,:,1]=imb
            im2[:,:,2]=imc

            imsave("im%i_%i.png" % (ii+startx,jj+starty), im2)
            
            if ii+startx==0 and jj+starty==0:
                #print(im[(ima==0) &( imc==0) & (im>64)])
                print(np.max(imb[(ima==0)&(imc==0)]))
                #raise
    
        #stitching
        xlist=[]
        ylist=[]
        for file in os.listdir():
            if file.startswith('im') and file.count('_') and file.count('.png'):
                #print(file)
                buf=re.split("_|\.",file)
                #print(buf)
                xpos=eval(buf[0].replace("im",""))
                ypos=eval(buf[1])
                xlist.append(xpos)
                ylist.append(ypos)

        #print( max(xlist))
    if display==1:
        new_im = Image.new('RGB', (max(xlist)-min(xlist)+1024,max(ylist)-min(ylist)+1024), (250,250,250))
        for jj in range( min(ylist), max(ylist)+1024, 1024):
            for ii in range( min(xlist), max(xlist)+1024, 1024):
            
                if os.path.exists("im%i_%i.png" % (ii,jj)):
                    img = Image.open("im%i_%i.png" % (ii,jj) )
                    print(ii,jj,img.size)
                    #new_im = Image.new('RGB', (2*img.size[0],2*img.size[1]), (250,250,250))
                    #new_im.paste(img, (ii-min(xlist),jj-min(ylist)))
                    new_im.paste(img, (jj-min(ylist),ii-min(xlist)))
                    
        new_im.save("merged_images.png", "PNG")
        
            
