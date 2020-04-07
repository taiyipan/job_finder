import random
import os

# human controls
false_data = True

# create temp list structure to hold data pairs
data = list()

# get file names for data pairs (only labeled dataset)
data_names_list = os.listdir('data/labels/')

# open and read each data pair into nested python list
for data_file_path in data_names_list:
    # generate path names
    feature_file_path = 'data/features/' + data_file_path
    label_file_path = 'data/labels/' + data_file_path
    # open both feature and label files
    with open(feature_file_path, 'r', encoding = 'utf8') as features, open(label_file_path, 'r', encoding = 'utf8') as labels:
        count = 0
        # read 1 label and 1 feature each step
        for line in labels:
            label = int(line.strip())
            feature = str()
            for line in features:
                feature += line
                if '<<END>>' in line:
                    break
            # add data pair to python list as a tuple
            data.append((feature, label))
            count += 1
        print('Gathered {} data pairs from {}'.format(count, data_file_path))

# get files names for false data pairs (only falsely labeled dataset)
if false_data:
    data_names_list = os.listdir('false_data/labels/')

    # open and read each data pair into nested python list
    for data_file_path in data_names_list:
        # generate path names
        feature_file_path = 'false_data/features/' + data_file_path
        label_file_path = 'false_data/labels/' + data_file_path
        # open both feature and label files
        with open(feature_file_path, 'r', encoding = 'utf8') as features, open(label_file_path, 'r', encoding = 'utf8') as labels:
            count = 0
            # read 1 label and 1 feature each step
            for line in labels:
                label = int(line.strip())
                feature = str()
                for line in features:
                    feature += line
                    if '<<END>>' in line:
                        break
                # add data pair to python list as a tuple
                data.append((feature, label))
                count += 1
            print('Gathered {} data pairs from {}'.format(count, data_file_path))

# shuffle data
random.shuffle(data)
print('Data shuffled')

# save shuffled data
data_path = '/home/taiyi/job_finder/binary_classifier/data/'
feature_data_path = data_path + 'features.txt'
label_data_path = data_path + 'labels.txt'
with open(feature_data_path, 'w') as features, open(label_data_path, 'w') as labels:
    while data:
        pair = data.pop()
        features.write(pair[0])
        labels.write(str(pair[1]) + '\n')
print('Data saved')
