import sys
import math
import copy
import time

class_label_set = set()
g_prune_acc = 0

class Node:
    def __init__(self, value, size):
        self.value = value
        self.true = None
        self.false = None
        self.size = size
        self.parent = None
    def __str__(self):
        return str(self.value)
    def add_true(self, node):
        self.true = node
    def add_false(self, node):
        self.false = node
    def add_parent(self, node):
        self.parent = node

# compare node return 0 if they are same, return 1 otherwise
def cmp_node(a,b):
    if (a.value == b.value):
        if (a.true.value == b.true.value) and (a.false.value == b.false.value):
            if (a.size == b.size) and (a.parent.value == b.parent.value):
                if (a.true.size == b.true.size) and (a.false.size == b.false.size):
                    return 0
    return 1

# Preprocess the data
def pre_processing(file_name):
    temp_dict = dict()
    class_set = set()
    f = open(file_name,"r")
    for lines in list(f):
        lines = lines.strip('\n')
        temp = lines.split(', ')
        for i in range(0, len(temp)-1):
            if temp[i] in temp_dict:
                temp_dict[temp[i]] += 1
            else:
                temp_dict[temp[i]] = 0
        class_label_set.add(temp[-1])
    dict_sorted = sorted(temp_dict, key=temp_dict.get, reverse=True)
    header = []
    for s in dict_sorted:
        header.append(s)
    header.append("class_label")
    new_data = []
    new_data.append(header)
    f.close()
    f = open(file_name,"r")
    for lines in list(f):
        lines = lines.strip('\n')
        temp = lines.split(', ')
        temp_data = []
        for i in range(0, len(new_data[0])-1):
            temp_data.append(False)
        for i in range(0, len(temp)-1):
            index = new_data[0].index(temp[i])
            temp_data[index] = True
        temp_data.append(temp[-1])
        new_data.append(temp_data)
    f.close()
    return new_data

def class_ent(data):
    ent = 0.0
    total = 0.0
    temp_dict = dict.fromkeys(class_label_set, 0.0)
    for i in range(1, len(data)):
        temp_dict[data[i][-1]] += 1
        total += 1
    for d in temp_dict:
        val = temp_dict[d]
        ent -= (val/total) * math.log((val/total), 2)
    return ent

def Entropy(data, value):
    ent = 0.0
    true = 0.0
    false = 0.0
    index = data[0].index(value)
    for i in range(1, len(data)):
        if data[i][index]:
            true += 1
        else:
            false += 1
    total = len(data) - 1.0
    if true == 0 or false == 0:
        return 0
    ent -= ((true/total * math.log((true/total), 2)) +
            (false/total * math.log((false/total), 2)))

    return ent

def get_most_common(data, prev_label):
    temp_dic = dict.fromkeys(class_label_set, 0)
    for a in range(1, len(data)):
        temp_dic[data[a][-1]] += 1
    if prev_label is None:
        most_common = ""
        mc = 0
        for q in temp_dic:
            if mc < temp_dic[q]:
                most_common = q
                mc = temp_dic[q]
        return most_common
    else:
        temp_list = []
        for q in temp_dic:
            temp_list.append(q)
            temp_list.append(temp_dic[q])
        if temp_list[1] == temp_list[3]:
            return prev_label
        elif temp_list[1] > temp_list[3]:
            return temp_list[0]
        else:
            return temp_list[2]

def ID3(data1, att, prev, depth, is_limit, prev_label):
    # copy data set.
    data = copy.deepcopy(data1)
    # delete the attribute was added to a tree node.
    if att is not None:
        att_index = data[0].index(att)
        for i in range(0, len(data)):
            del data[i][att_index]
    # get most common label.
    most_common = get_most_common(data, prev_label)
    # return once all data was evaluated.
    if len(data) == 1:
        return None
    if len(data[0]) == 1:
        return Node(most_common, len(data) - 1)
    # return a single node if all instance have same label
    c_l = set()
    for i in range(1, len(data)):
        c_l.add(data[i][-1])
    if len(c_l) < 2:
        return Node(data[1][-1], len(data) - 1)
    else:
        index = 0
        max = 0
        ent = 0
        # find best attribute
        for i in range(0, len(data[0]) - 1):
            # gain
            k = Entropy(data,data[0][i])
            temp_g = prev - k
            if max < temp_g:
                max = temp_g
                ent = k
                index = i
        root = Node(data[0][index], len(data) - 1)
        
        values = {True, False}

        temp_depth = depth + 1

        # get sub_set
        sub_set_true = []
        sub_set_false = []
        sub_set_true.append(data[0])
        sub_set_false.append(data[0])

        for ii in range(1, len(data)):
            if data[ii][index]:
                sub_set_true.append(data[ii])
            else:
                sub_set_false.append(data[ii])

        # maxDepth
        if is_limit != 0:
            if temp_depth == is_limit:
                t_node = None
                f_node = None
                if len(sub_set_true) < 2:
                    t_node = Node(most_common, 0)
                else:
                    t_common = get_most_common(sub_set_true, most_common)
                    t_node = Node(t_common, len(sub_set_true) - 1)
                if len(sub_set_false) < 2:
                    f_node = Node(most_common, 0)
                else:
                    f_common = get_most_common(sub_set_false, most_common)
                    f_node = Node(f_common, len(sub_set_false) - 1)
                t_node.add_parent(root)
                f_node.add_parent(root)
                root.add_true(t_node)
                root.add_false(f_node)
                return root

        if len(sub_set_true) < 2:
            true_node = Node(most_common,0)
            true_node.add_parent(root)
            root.add_true(true_node)
        else:
            true_node = ID3(sub_set_true, root.value, ent, temp_depth, is_limit, most_common)
            true_node.add_parent(root)
            root.add_true(true_node)

        if len(sub_set_false) < 2:
            false_node = Node(most_common,0)
            false_node.add_parent(root)
            root.add_false(false_node)
        else:
            false_node = ID3(sub_set_false, root.value, ent, temp_depth, is_limit, most_common)
            false_node.add_parent(root)
            root.add_false(false_node)
        return root

def search(root, instance, header):
    if (root.true is not None and root.false is not None):
        index = header.index(root.value)
        if instance[index]:
            return search(root.true, instance, header)
        else:
            return search(root.false, instance, header)
    else:
        if root.value == instance[-1]:
            return 1.0
        else:
            return 0.0
            
def testing(data,model):
    match = 0.0
    total = 0.0
    for i in range(1, len(data)):
        instance = data[i]
        match += search(model, instance, data[0])
        total += 1.0
    return match/total

def post_pruning(val_set, model, accuracy):
    root = copy.deepcopy(model)
    queue = []
    queue.append(root)
    leaf_nodes = []
    # get the leaf nodes
    while len(queue) > 0:
        temp_root = queue[0]
        del queue[0]
        if temp_root.true.value not in class_label_set:
            queue.append(temp_root.true)
        if temp_root.false.value not in class_label_set:
            queue.append(temp_root.false)
        if (temp_root.true.value in class_label_set) and (temp_root.false.value in class_label_set):
            leaf_nodes.append(temp_root)

    for i in range(0,len(leaf_nodes)):
        temp_leaf = leaf_nodes[i]
        while(1):
            if temp_leaf.parent is None:
                break
            parent = temp_leaf.parent
            m_c = None
            is_true = 0
            if temp_leaf.true.size > temp_leaf.false.size:
                m_c = temp_leaf.true
            else:
                m_c = temp_leaf.false
            m_c.size = temp_leaf.size
            if cmp_node(parent.true,temp_leaf) == 0:
                is_true = 1
                parent.add_true(m_c)
            else:
                parent.add_false(m_c)
            temp_ac = testing(val_set,root)
            if temp_ac < accuracy:
                if is_true == 1:
                    parent.true = temp_leaf
                else:
                    parent.false = temp_leaf
                break
            else:
                temp_leaf = parent
                accuracy = temp_ac
    return root

# post_pruning
def prune(root, model, val_set, acc):
    if root.true.value not in class_label_set:
        prune(root.true, model, val_set, acc)
    if root.false.value not in class_label_set:
        prune(root.false, model, val_set, acc)
    if (root.true.value in class_label_set) and (root.false.value in class_label_set):
        #print("true.value: ",root.true.value," false: ",root.false.value)
        if root.parent is None:
            return
        parent = root.parent
        most_common = None
        is_true = 0
        if root.true.size > root.false.size:
            most_common = root.true
        else:
            most_common = root.false
        most_common.size = root.size
        if cmp_node(parent.true, root) == 0:
            is_true = 1
            parent.add_true(most_common)
        else:
            parent.add_false(most_common)
        temp_ac = testing(val_set,model)
        if temp_ac < acc:
            if is_true == 1:
                parent.true = root
            else:
                parent.false = root

# printing decision tree
def print_model(model):
    queue1 = []
    queue2 = []
    num_node = 0;
    queue1.append(model)
    while (len(queue1) > 0 or len(queue2) > 0):
        if len(queue1) > 0:
            while len(queue1) > 0:
               s = queue1[0]
               print(s.value,end =" ")
               if s.true is not None and s.false is not None:
                   queue2.append(s.true)
                   queue2.append(s.false)
               del queue1[0]
               num_node += 1
        print()
        if len(queue2) > 0:
            while len(queue2) > 0:
               s = queue2[0]
               print(s.value,end =" ")
               if s.true is not None and s.false is not None:
                   queue1.append(s.true)
                   queue1.append(s.false)
               del queue2[0]
               num_node += 1
        print()
    print()

# printing number of nodes
def num_node(root):
    count = 1
    if root.true is not None:
        count += num_node(root.true)
    if root.false is not None:
        count += num_node(root.false)
    return count

"""
def baseline(data, most):
    match = 0.0
    for s in data:
        if s[-1] == most:
            match += 1
    total = len(data)-1
    return match/total
"""
def main():
    train_data = pre_processing(sys.argv[1])
    test_data = pre_processing(sys.argv[2])
    mode = sys.argv[3]
    fourth = int(sys.argv[4])
    fourth = int((fourth * (len(train_data)-1)) / 100)
    fifth = 0
    sixth = 0
    if mode != "vanilla":
        fifth = 100 - int(sys.argv[5])
        fifth = int((fifth * (len(train_data)-1)) / 100)
        if mode == "maxDepth":
            sixth = int(sys.argv[6])
    model = None
    train_data1 = train_data[:fourth + 1]
    class_entropy = class_ent(train_data1)
    c_most_common = get_most_common(train_data1, None)
    if mode == "vanilla":
        model = ID3(train_data1, None, class_entropy, 0, 0, c_most_common)
    elif mode == "prune":
        model = ID3(train_data1, None, class_entropy, 0, 0, c_most_common)
        val_set = train_data[fifth + 1:]
        val_set.insert(0,train_data[0])
        g_prune_acc = testing(val_set, model)
        # prune while new acc is not decrease
        while (1):
            prune(model, model, val_set, g_prune_acc)
            new_acc = testing(val_set, model)
            if new_acc > g_prune_acc:
                g_prune_acc = new_acc
            else:
                break
    else:
        model = ID3(train_data1, None, class_entropy, 0, sixth, c_most_common)
    train_set_accuracy = testing(train_data1, model)
    test_set_accuracy = testing(test_data, model)
    print("Train set accuracy: ", train_set_accuracy) 
    print("Test set accuracy: ", test_set_accuracy)
    #print_model(model)
    print("num nodes: ",num_node(model))

start_time = time.time()
main()
print("--- %s seconds ---" % (time.time() - start_time))
