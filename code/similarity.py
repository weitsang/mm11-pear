import os
import math
import numpy
from numpy import *
import Gnuplot
import types
from scipy import *
from scipy import linalg,stats
import sys
#import matplotlib.pyplot as plt
import Polygon
import Polygon.IO

#python similarity_3_4.py file.txt > peernumber.txt

#######################################compute the overlapped area of two view frustums' cross-sections
def polygonshare(a,b,beta,farpdist):         
    x1,y1,a1,x2,y2,a2=a[1],a[2],a[4],b[1],b[2],b[4]
    p1=(x1,y1)
    if a1<=180:
       rad1=pi*(a1-beta)/180
       rad2=pi*(a1+beta)/180
    else:
       rad1=pi*(360-a1-beta)/180*-1
       rad2=pi*(360-a1+beta)/180*-1
    p2=(cos(rad1)*farpdist/cos(pi*beta/180)+x1,sin(rad1)*farpdist/cos(pi*beta/180)+y1)
    p3=(cos(rad2)*farpdist/cos(pi*beta/180)+x1,sin(rad2)*farpdist/cos(pi*beta/180)+y1)
    polygon1=Polygon.Polygon((p1,p2,p3))
    pg1=str(p1[0])+' '+str(p1[1])+'\t'+str(p2[0])+' '+str(p2[1])+'\t'+str(p3[0])+' '+str(p3[1])
    p1=(x2,y2)
    if a2<=180:
       rad1=pi*(a2-beta)/180
       rad2=pi*(a2+beta)/180
    else:
       rad1=pi*(360-a2-beta)/180*-1
       rad2=pi*(360-a2+beta)/180*-1
    p2=(cos(rad1)*farpdist/cos(pi*beta/180)+x2,sin(rad1)*farpdist/cos(pi*beta/180)+y2)
    p3=(cos(rad2)*farpdist/cos(pi*beta/180)+x2,sin(rad2)*farpdist/cos(pi*beta/180)+y2)
    polygon2=Polygon.Polygon((p1,p2,p3))
    pg2=str(p1[0])+' '+str(p1[1])+'\t'+str(p2[0])+' '+str(p2[1])+'\t'+str(p3[0])+' '+str(p3[1])
    polygon3=polygon1 & polygon2
    return (polygon3.area(),pg1,pg2)

##########################initiate variables

fr = open(sys.argv[1],'r')
#line = fr.readline() #column title line
line = fr.readline()
list0 = line.split()[1]

fw = open('sml&ang_'+sys.argv[1],'w')
fw2 = open('frustum_'+sys.argv[1],'w')

paircount = 0    #count the total number of pairs 
#dirlimpair = 0   #the number of pairs filtered out by direction threshold
#fov = float(sys.argv[2])  #field of view of the camera
fov = 60
farpdist = 256.0  #*******farpdist=float(sys.argv[3])
aspect = 640.0/480.0
longsidehalf = farpdist*tan(pi*0.5*fov/180)*aspect  #half of the long side of the farplane
viewangle = arctan(longsidehalf/farpdist)/pi*180*2  #horizontal viewangle of the camera
vsml_thresh = 0.0   #*******vsml_thresh=float(sys.argv[4])
cross_sectional_area = 0.5*farpdist*2*farpdist*tan(pi*viewangle/2/180) #cross sectional area of the frustum
#similarity = []  #record similarity values of each pair
#######record peers of each avatar under different similarity thresholds
cnt1={}
cnt2={}
cnt3={}
cnt4={}
cnt5={}
seccnt={}  #count the appearance times of each avatar 

#print sys.argv[1],"with field of view",sys.argv[2]
while (line.strip()!=""):
  list1=[i for i in line.split()]
  list2=list1[1]
  arraytemp=[]
  while list2==list0:
    array1=[float(i) for i in list1[2:len(list1)]]
    arraytemp.append(array1)
    if (array1[0] in cnt1)!=True:
       cnt1[array1[0]]=0
       cnt2[array1[0]]=0
       cnt3[array1[0]]=0
       cnt4[array1[0]]=0
       cnt5[array1[0]]=0
       seccnt[array1[0]]=0
    seccnt[array1[0]]=seccnt[array1[0]]+1
    line=fr.readline()
    list1=[i for i in line.split()]
    if line!="":
       list2=list1[1]
    else:
       list2=[]
  list0=list2
  length=len(arraytemp)
  j=1
  for a in arraytemp[:length-1]:
    for b in arraytemp[j:length]:
      ang=abs(a[4]-b[4])
      if ang>180:
         ang=abs(360-ang)
      (area,polygon1,polygon2)=polygonshare(a,b,viewangle/2,farpdist)     
      vsml=area/cross_sectional_area
      if ang>viewangle:
         vsml=0.0
 #     similarity.append(vsml)
      fw.write(str(vsml)+'\t'+str(ang)+'\n')
      if vsml>0:
         cnt1[a[0]]=cnt1[a[0]]+1
         cnt1[b[0]]=cnt1[b[0]]+1
      if vsml>0.3:
         cnt2[a[0]]=cnt2[a[0]]+1
         cnt2[b[0]]=cnt2[b[0]]+1
      if vsml>0.5:
         cnt3[a[0]]=cnt3[a[0]]+1
         cnt3[b[0]]=cnt3[b[0]]+1
      if vsml>0.7:
         cnt4[a[0]]=cnt4[a[0]]+1
         cnt4[b[0]]=cnt4[b[0]]+1
      if vsml>0.9:
         cnt5[a[0]]=cnt5[a[0]]+1
         cnt5[b[0]]=cnt5[b[0]]+1
      paircount=paircount+1
      fw2.write(str(paircount)+'\t'+str(vsml)+'\t'+polygon1+'\t'+polygon2+'\n')
    j=j+1
#Polygon.IO.writeGnuplotTriangles('tri.txt',polygons)

#print "Total number of pairs is",paircount
#print "Number of pairs with direction limit is",dirlimpair
#ratio=dirlimpair*1.0/paircount
#print "The ratio is","%.2g" % ratio

for k in cnt1.keys():
	print k,"\t%.1f\t%.1f\t%.1f\t%.1f\t%.1f" % (cnt1[k]*1.0/seccnt[k],cnt2[k]*1.0/seccnt[k],cnt3[k]*1.0/seccnt[k],cnt4[k]*1.0/seccnt[k],cnt5[k]*1.0/seccnt[k])

fw.close()
fw2.close()
fr.close()
