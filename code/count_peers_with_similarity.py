# similarity_bin.py
# --
# This code is a split off the original MM'11 similarity.py so that all similarities are logged and binning is done separately.
# This script performs binning.
#
# The script takes the output from similarity.py as input.
# Each line of an input contains information from an avatar's point of view at a particular time instance.
# The line contains <time stamp> <avatar ID> <number of neighbors> <number of neighbors with zero similarity> <similarity 1> <similarity 2> ...
#
# This script simply counts, for each avatar, how many percent of neighbors have similarity over 0.9, 0.7, 0.5, 0.3, and 0.1 (over all time)
# (In the original script, this output is called "peernum")
#
# Original Author: Minhui Zhu
# Maintainer: Wei Tsang Ooi
#
#--
import fileinput

THRESHOLDS = [0,0.3,0.5,0.7,0.9];
avatars = []
counter = {}
for line in fileinput.input():
	line = line.split()
	avatar_id = line[1] 
	num_of_neighbors = int(line[2])

	if avatar_id not in avatars:
		# if this is the first time we see this avatar,
		# initialize the counters.
		avatars.append(avatar_id);
		for x in THRESHOLDS:
			counter[avatar_id,x] = 0
		counter[avatar_id,"total"] = 0

  # count the number of time slot where this avatar appears in.
	counter[avatar_id,"total"] += 1

	# making multiple passes here.  Could be optimize, but this code is short..
	line = [float(i) for i in line]
	for x in THRESHOLDS:
		for similarity in line[4:len(line)]:
			if similarity > x:
				counter[avatar_id,x] += 1

# Finally, output the average number of neighbors 
# (over all time slot the avatar appears in) where 
# similarity is > x
for avatar_id in sorted(avatars, key=int):
	output = "%d" % int(avatar_id)
	for x in THRESHOLDS:
		output += "\t%.1f" % (counter[avatar_id,x]*1.0/counter[avatar_id,"total"]);
	print output
