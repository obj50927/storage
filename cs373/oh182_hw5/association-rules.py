# Byoungjin Oh
# PUID: 0030411229

import sys
import random
import pandas as pd
import numpy as np
import math
import time
import copy
import itertools

fr = dict()

# class
class node:
    def __init__(self, ant, con):
        self.ant = ant
        self.con = con
    def __str__(self):
        return str(self.ant) + "->" + str(self.con)
    def __repr__(self):
        return str(self.ant) + "->" + str(self.con)

# Read file
def read_file(file_name):
    df = pd.read_csv(file_name)
    for col in df.columns:
        if (len(df[col].unique())>2):
            for att in df[col].unique():
                df[str(att)] = [1 if x == att else 0 for x in df[col]]
            del df[col]
        else:
            df[col] = df[col].map({True: 1, False: 0})
    return df

# FrequentItemsetGeneration
def FrequentItemsetGeneration(df, minsup):
    total = len(df)
    L = []

    for col in df.columns:
        frequncy = len(df[df[col]==1])/total
        if frequncy < minsup:
            del df[col]
        else:
            fr[col] = frequncy
    First = []
    for col in df.columns:
        First.append([col])
    First.sort()
    L.append(First)
    k = 0
    while(1):
        C = CandidateItemsetGeneration(L[k], minsup)
        tempL = []
        for c1 in C:
            tempdf = df
            for c2 in c1:
                tempdf = tempdf[tempdf[c2]==1]
            frequncy = len(tempdf)/total
            if frequncy > minsup:
                tempL.append(c1)
                str1 = ','.join(c1)
                fr[str1] = frequncy
        if len(tempL) < 1:
            break
        else:
            L.append(tempL)
        k += 1

    return L

# CandidateItemsetGeneration
def CandidateItemsetGeneration(Lk, minsup):
    C = []
    for i in range(len(Lk)):
        for j in range(len(Lk)):
            ttt = []
            for k in range(len(Lk[i])):
                if k < len(Lk[i])-1:
                    if Lk[i][k] == Lk[j][k]:
                        ttt.append(Lk[i][k])
                else:
                    if Lk[i][k] < Lk[j][k]:
                        ttt.append(Lk[i][k])
                        ttt.append(Lk[j][k])
                        if len(ttt) == len(Lk[i]) + 1:
                            C.append(ttt)
    C.sort()
    C = list(C for C,_ in itertools.groupby(C))
    for c in C:
        for i in range(len(c)):
            temp = copy.deepcopy(c)
            del temp[i]
            if temp not in Lk:
                C.remove(c)
                break
    return C

def RuleGeneration(L, minconf):
    R = []
    for i in range(1,len(L)):
        tempR = []
        for e in L[i]:
            key1 = ','.join(e)
            queue = []
            queue.append(node(e,[]))
            while(len(queue)>0):
                q = queue[0]
                Antecedent = copy.deepcopy(q.ant)
                del queue[0]
                for t in range(len(Antecedent)):
                    temp = copy.deepcopy(Antecedent)
                    consequent = copy.deepcopy(q.con)
                    consequent.append(temp[t])
                    del temp[t]
                    if len(temp) > 0:
                        key2 = ','.join(temp)
                        if fr[key1]/fr[key2] > minconf:
                            n = node(temp,consequent)
                            queue.append(n)
                            tempR.append(n)
        R.append(tempR)
    return R
            


start_time = time.time()

df = read_file(sys.argv[1])
#df = df[:3]
minsup = float(sys.argv[2])
minconf = float(sys.argv[3])
#print(len(df.columns))

L = FrequentItemsetGeneration(df, minsup)
R = RuleGeneration(L, minconf)
for k in range(1,len(L)):
    print("FREQUENT-ITEMS ", k+1, " ", len(L[k]))
for k in range(len(R)):
    print("ASSOCIATION-RULES ", k+2, " ", len(R[k]))
print("--- %s secondes ---" % (time.time() - start_time))
