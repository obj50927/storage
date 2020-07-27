# Byoungjin Oh
# PUID: 0030411229

import sys
import random
import pandas as pd
import numpy as np
import math
import time
import copy

# Read file
def read_file(file_name):
    data = pd.read_csv(file_name)
    return data

# Euclidean distance
def distance(row, center):
    dist = 0
    for i in range(0,4):
        dist += pow((row[i] - center[i]), 2)
    dist = math.sqrt(dist)
    return dist

# Manhattan distance
def m_distance(row, center):
    dist = 0
    for i in range(0,4):
        dist += abs(row[i] - center[i])
    return dist

# Update centroids
def cent(data, center):
    for i in range(0,4):
        center[i] = (data.iloc[:,i].sum()/len(data.index))

# Within-cluster distance
def wcf(data, Centroids):
    wc = 0
    for i in range(len(Centroids)):
        for row in data[data.Group == i+1].iterrows():
            dist = 0
            if option == '4':
                dist = m_distance(row[1],Centroids[i])
            else:
                dist = distance(row[1],Centroids[i])
            wc += pow(dist,2)
    return wc

# Between-cluster distance
def bcf(Centroids):
    bc = 0
    for c1 in Centroids:
        for c2 in Centroids:
            dist = 0
            if option == '4':
                dist = m_distance(c1,c2)
            else:
                dist = distance(c1,c2)
            bc += pow(dist,2)
    return bc

start_time = time.time()

data = read_file("../data/given/"+sys.argv[1])
#data = data[:100]
k = sys.argv[2]
option = sys.argv[3]
data = data[['latitude','longitude','reviewCount','checkins']]

if option == '2':
    data.loc[:,'reviewCount'] = np.log2(data['reviewCount'])
    data.loc[:,'checkins'] = np.log2(data['checkins'])

if option == '3' or option == '6':
    data.loc[:,'latitude'] -= np.mean(data['latitude'])
    data.loc[:,'longitude'] -= np.mean(data['longitude'])
    data.loc[:,'reviewCount'] -= np.mean(data['reviewCount'])
    data.loc[:,'checkins'] -= np.mean(data['checkins'])
    data.loc[:,'latitude'] /= np.std(data['latitude'])
    data.loc[:,'longitude'] /= np.std(data['longitude'])
    data.loc[:,'reviewCount'] /= np.std(data['reviewCount'])
    data.loc[:,'checkins'] /= np.std(data['checkins'])

trial = 1

if option == '5':
    data = data.sample(frac=0.06)
    data.index = range(len(data))
    trial = 5

for t in range(trial):
    data['Group'] = 0
    data_length = len(data.index)
    #print(data)
    Centroids = []
    for i in range(0,int(k)):
        Centroids.append([0,0,0,0])

    for i in range(1,int(k)+1):
        while(1):
            ran = random.randint(0,data_length-1)
            if (data.loc[ran,['Group']] == 0).bool():
                data.loc[ran, ['Group']] = i
                Centroids[i-1][0] = data.loc[ran, ['latitude']].values[0]
                Centroids[i-1][1] = data.loc[ran, ['longitude']].values[0]
                Centroids[i-1][2] = data.loc[ran, ['reviewCount']].values[0]
                Centroids[i-1][3] = data.loc[ran, ['checkins']].values[0]
                break

    while (1):
        #print(len(data[data.Group == 0]))
        for row in data.iterrows():
            mins = [0,99999999]
            for i in range(len(Centroids)):
                dist = 0
                if option == '4':
                    dist = m_distance(row[1],Centroids[i])
                else:
                    dist = distance(row[1],Centroids[i])
                if mins[1] > dist:
                    mins[0] = i + 1
                    mins[1] = dist
            data.loc[row[0], ['Group']] = mins[0]
        temp_cent = copy.deepcopy(Centroids)
        for i in range(len(Centroids)):
            cent(data[data.Group == i+1], Centroids[i])

        if temp_cent == Centroids:
            break
    
    wc = wcf(data,Centroids)
    bc = bcf(Centroids)
    if option == '6':
        print("SSE=", bc/wc)
    else:
        print("WC-SSE=", wc)

    temp = [[],[],[],[]]
    for kk in range(len(Centroids)):
        for i in range(len(Centroids[kk])):
            temp[i].append(Centroids[kk][i])
        print("Centroid",kk+1,Centroids[kk])
    # for i in temp:
    #     print("-----")
    #     print(i)
#print(data)
#print("--- %s secondes ---" % (time.time() - start_time))
