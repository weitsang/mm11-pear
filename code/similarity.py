# similarity.py
# --
# This script takes an input SL trace, an optional fov (default is 60 degree),  
# a far plane distance (default is 256), and output either the visual similarity 
# (default) or the angle difference between every pair of avatars at every time 
# instance.
#
# When visual similarity is printed, the script will print to stdout.  
# Each line in the output contains
# <time id> <avatar ID> <num_of_neighbors> <num_of_zeros> <similarity1> <similarity2> ..
# 
# When angle difference is printed, the script will print to stdout.  
# Each line in the output contains
# <time id> <avatar ID> <num_of_neighbors> <angle diff 1> <angle diff 2> ..
# 
# Example usage:
#   python similarity.py --output=angle-diff trace.txt 
#   python similarity.py --output=similarity trace.txt 
#   python similarity.py --fov=80 trace.txt 
#   python similarity.py --far-plane=64 trace.txt 
#
# Original Author: Minhui Zhu, 2010-03-12
# Maintainer: Wei Tsang Ooi, 2013-05-21

import os
import math
import numpy
import types
import sys, getopt
import Polygon
from numpy import *

def get_left_right_angle(view_angle, beta):
    if view_angle<=180:
       rad1=pi*(view_angle-beta)/180
       rad2=pi*(view_angle+beta)/180
    else:
       rad1=pi*(360-view_angle-beta)/180*-1
       rad2=pi*(360-view_angle+beta)/180*-1
    return rad1, rad2

def get_triangle_point(angle, beta, farpdist, x, y):
    return (cos(angle)*farpdist/cos(pi*beta/180)+x,sin(angle)*farpdist/cos(pi*beta/180)+y)

def triangle_to_string(p1, p2, p3):
    return str(p1[0])+' '+str(p1[1])+'\t'+str(p2[0])+' '+str(p2[1])+'\t'+str(p3[0])+' '+str(p3[1])

# compute the overlapped area of two view frustums' cross-sections
def get_overlapped_area(avatar1, avatar2, beta, farpdist):         
    x1, y1, a1 = avatar1[1], avatar1[2], avatar1[4]
    x2, y2, a2 = avatar2[1], avatar2[2], avatar2[4]
    p1 = (x1,y1)
    rad1, rad2 = get_left_right_angle(a1, beta)
    p2 = get_triangle_point(rad1, beta, farpdist, x1, y1)
    p3 = get_triangle_point(rad2, beta, farpdist, x1, y1)
    polygon1 = Polygon.Polygon((p1,p2,p3))
    pg1 = triangle_to_string(p1, p2, p3)

    p1 = (x2,y2)
    rad1, rad2 = get_left_right_angle(a2, beta)
    p2 = get_triangle_point(rad1, beta, farpdist, x2, y2)
    p3 = get_triangle_point(rad2, beta, farpdist, x2, y2)
    polygon2 = Polygon.Polygon((p1,p2,p3))
    pg2 = triangle_to_string(p1, p2, p3)

    overlap = polygon1 & polygon2
    return (overlap.area(),pg1,pg2)

paircount = 0    #count the total number of pairs 

# field of view of the camera
options, args = getopt.gnu_getopt(sys.argv, '', ["fov=","far-plane=","output="])

# default options
fov = 60
farpdist = 256.0  
output = "similarity"

for key, value in options:
  if key == "--fov":
    fov = float(value)
  elif key == "--far-plane":
    farpdist = float(value)
  elif key == "--output":
    if value in ['similarity','angle-diff']:
      output = value
    else:
      print "Error: unknown output format: should be either 'similarity' or 'angle-diff'"

aspect = 640.0/480.0

# Half of the long side of the farplane
longsidehalf = farpdist*tan(pi*0.5*fov/180)*aspect  

# Horizontal viewangle of the camera
viewangle = arctan(longsidehalf/farpdist)/pi*180*2  

# Cross sectional area of the frustum
cross_sectional_area = 0.5*farpdist*2*farpdist*tan(pi*viewangle/2/180) 

# Open the avatar mobility trace (filename is given as the first
# argument in the command line)
avatar_trace = open(args[1],'r')

# Start readin the trace, line-by-line.
time_code = 0
line = avatar_trace.readline()
prev_time = line.split()[1]
while (line.strip()!=""):
  curr_line = line.split()
  curr_time = curr_line[1]
  items_at_this_time = []
  while curr_time == prev_time:
    curr_items = [float(i) for i in curr_line[2:len(curr_line)]]
    items_at_this_time.append(curr_items)
    avatar_id = curr_items[0]
    line = avatar_trace.readline()
    curr_line = line.split()
    if line != "":
       curr_time = curr_line[1]
    else:
       curr_time = []
  prev_time = curr_time
  time_code = time_code + 1

  num_of_avatars = len(items_at_this_time)

  # initialize a list of visual similarity numbers
  visual_similarities = {}
  angle_diffs = {}
  zero_count = {}
  for i in range(0,num_of_avatars):
    avatar_id = items_at_this_time[i][0]
    visual_similarities[avatar_id] = []
    angle_diffs[avatar_id] = []
    zero_count[avatar_id] = 0

  for i in range(0,num_of_avatars-1):
    avatar1 = items_at_this_time[i]
    # for a pair (a,b), we compute the similarity twice!
    # could be optimize here.
    for j in range(i+1,num_of_avatars):
      avatar2 = items_at_this_time[j]
      angle_diff = abs(avatar1[4] - avatar2[4])
      angle_diffs[avatar1[0]].append(angle_diff);
      angle_diffs[avatar2[0]].append(angle_diff);
      if angle_diff > 180:
        angle_diff = abs(360-angle_diff)
      if angle_diff > viewangle:
        zero_count[avatar1[0]] += 1
        zero_count[avatar2[0]] += 1
      else:
        area,p1,p2 = get_overlapped_area(avatar1,avatar2,viewangle/2,farpdist)     
        vsml = area/cross_sectional_area
        visual_similarities[avatar1[0]].append(vsml);
        visual_similarities[avatar2[0]].append(vsml);

# Print similarity
if output == "similarity":
  for avatar_id in visual_similarities:
    output = "%d\t%d\t%d\t%d" % (time_code, avatar_id, num_of_avatars, zero_count[avatar_id])
    for similarity in visual_similarities[avatar_id]:
      output += '\t' + str(similarity)
    print output

# Print angle difference
elif output == "angle-diff":
  for avatar_id in angle_diffs:
    output = "%d\t%d\t%d" % (time_code, avatar_id, num_of_avatars) 
    for diff in angle_diffs[avatar_id]:
      output += '\t' + str(diff)
    print output

avatar_trace.close()
# vim:expandtab:sw=2
