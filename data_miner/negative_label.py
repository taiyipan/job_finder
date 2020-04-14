import os

# get files names for false data features
negatives = os.listdir('false_data/features/')

# loop through files
for negative in negatives:
    # generate path names
    feature_path = 'false_data/features/' + negative
    label_path = 'false_data/labels/' + negative
    # open both files
    with open(feature_path, 'r', encoding = 'utf8') as feature, open(label_path, 'w', encoding = 'utf8') as label:
        # count samples
        count = 0
        for line in feature:
            if '<<END>>' in line:
                count += 1
        # create negative labels
        for i in range(count):
            label.write('0\n')
        # display results
        print('{} negative labels applied for {}'.format(count, negative))
