# Byoungjin Oh 0030411229



import csv
import re
import sys
import random

# add None to missing value
def my_None(s):
    if not s:
        s = "None"
    return s

#trim string
def my_trim(row,index,sets):
    row[index] = row[index].strip('[]');
    row[index] = re.findall(r"[\w-]+",row[index]);
    for s in row[index]:
        sets.add(s)

#add column
def add_column(row, sets, index, rows):
    for e in sets:
        if rows == 0:
            row.append(e)
        else:
            t = e in row[index]
            if t:
                row.append("True")
            else:
                row.append("False")

#open file
def pre_processing(file_name):
    data = []
    reco_set = set();
    reco_index = -1;
    ambience_set = set();
    ambience_index = -1;
    parking_set = set();
    parking_index = -1;
    dR_set = set();
    dR_index = -1;
    Y_index = -1;
    with open('yelp_data.csv') as csvfile:
        readCSV = csv.reader(csvfile, delimiter=',');
        # read file
        rows = 0;
        for row in readCSV:
            if rows == 0:
                reco_index = row.index("recommendedFor");
                ambience_index = row.index("ambience");
                parking_index = row.index("parking");
                dR_index = row.index("dietaryRestrictions");
                Y_index = len(row)-1;
                rows += 1
            else:
                my_trim(row,reco_index,reco_set);
                my_trim(row,ambience_index,ambience_set);
                my_trim(row,parking_index,parking_set);
                my_trim(row,dR_index,dR_set);
                row = map(my_None, row);
            data.append(row)
        rows = 0;
        for row in data:
            add_column(row, reco_set, reco_index, rows)
            add_column(row, ambience_set, ambience_index, rows)
            add_column(row, parking_set, parking_index, rows)
            add_column(row, dR_set, dR_index, rows)
            rows += 1
        for row in data:
            row.append(row[Y_index])
            del row[Y_index]
            del row[reco_index]
            del row[dR_index]
            del row[parking_index]
            del row[ambience_index]
    
    return data

# nbc learning
def learning(data):
    set_list = [];
    for i in range(0,len(data[0])):
        set_list.append(set());

    for i in range(1,len(data)):
        for j in range(0,len(data[i])):
            if data[i][j] != "None":
                set_list[j].add(data[i][j])

    dic_list_T = []
    dic_list_F = []
    model_T = []
    model_F = []

    for i in range(0,len(set_list)):
        dic_list_T.append(dict.fromkeys(set_list[i],0))
        dic_list_F.append(dict.fromkeys(set_list[i],0))
        model_T.append(dict.fromkeys(set_list[i],0))
        model_F.append(dict.fromkeys(set_list[i],0))
    
    T = 0
    F = 0
    
    for i in range(1,len(data)):
        for j in range(0,len(data[i])):
            if data[i][j] != "None":
                if data[i][-1] == "True":
                    dic_list_T[j][data[i][j]] += 1
                else:
                    dic_list_F[j][data[i][j]] += 1
        if data[i][-1] == "True":
            T += 1
        else:
            F += 1
    
    for i in range(0,len(dic_list_T)-1):
        for att in dic_list_T[i]:
            if 0 in model_T[i].values():
                model_T[i][att] = float(dic_list_T[i][att] + 1.0) / (float(sum(dic_list_T[i].values()) + len(dic_list_T[i])))
            else:
                model_T[i][att] = float(dic_list_T[i][att]) / float(sum(dic_list_T[i].values()))
        for att in dic_list_F[i]:
            if 0 in model_F[i].values():
                model_F[i][att] = float(dic_list_F[i][att] + 1.0) / (float(sum(dic_list_F[i].values()) + len(dic_list_F[i])))
            else:
                model_F[i][att] = float(dic_list_F[i][att]) / float(sum(dic_list_F[i].values()))
    
    model_T.append(T)
    model_F.append(F)
    
    models = []
    models.append(model_T)
    models.append(model_F)

    return models

#evaluation
def eval(train,test, k):

    train_set = []
    test_set = []

    if k == 0:
        train_set = train
        test_set = test
    else:
        #cross-evaluation    
        train_set.append(train[0])
        test_set.append(train[0])
        for i in range(1,len(train)):
            if random.randint(0,100) < k:
                train_set.append(train[i])
            else:
                test_set.append(train[i])

    model = learning(train_set)
    model_T = model[0]
    model_F = model[1]
    T = float(model_T[-1])
    F = float(model_F[-1])
    zero_one = 0
    square = 0
    for i in range(1,len(test_set)):
        a = 1.0
        b = 1.0
        for j in range(0,len(test_set[i])-1):
            if test_set[i][j] != "None" and test_set[i][j] in model_T[j] and test_set[i][j] in model_F[j]:
                a *= model_T[j][test_set[i][j]]
                b *= model_F[j][test_set[i][j]]
        a *= T/(T+F)
        b *= F/(T+F)
        p = a/(a+b)
        
        if test_set[i][-1] == "True":
            y = 1
        else:
            y = 0;
        if p < 0.5 and y == 1:
            zero_one += 1
        elif p >= 0.5 and y == 0:
            zero_one += 1
        """if y == 1:
          square += (1 - ( a/(a+b) ))**2
        else:
          square += (1 - ( b/(a+b) ))**2"""
        square += (y-p)**2
    
            
    print("ZERO-ONE LOSS="+str(float(zero_one)/float(len(test_set))))
    print("SQUARED LOSS="+str(float(square)/float(len(test_set))))


def main():
    train_set = pre_processing(sys.argv[1])
    test_set = pre_processing(sys.argv[2])
    eval(train_set,test_set,0)


main() 
