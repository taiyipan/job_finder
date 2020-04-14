# get feature file name
name = 'junior_machine_learning_engineer_2020-03-31'

def generate_feature_path(name: str) -> str:
    return 'data/features/' + name + '.txt'
features_name = generate_feature_path(name)

# print seperation line
def seperation_line():
    CHAR = 200
    LINE = 3
    print('\n')
    for i in range(LINE):
        print(''.join('-' for i in range(CHAR)))
    print('\n')

# generate labels_name
def labels_name(features_name: str) -> str:
    tokens = features_name.split('.')
    tokens[0] = tokens[0].replace('features', 'labels')
    return tokens[0] + '.txt'
labels_name = labels_name(features_name)

# open features and labels
features = open(features_name, 'r')
print('Opening', features_name)
labels = open(labels_name, 'a')
print('Opening', labels_name)

# count labels
labels_count = 0
with open(labels_name, 'r') as labels_r:
    for line in labels_r:
        if '1' in line or '0' in line:
            labels_count += 1
print('Current labels:', labels_count)

# read features to match labels_count
features_count = 0
show = False
for line in features:
    # when current features_count matches labels_count
    if features_count == labels_count and not show:
        show = True
        print('Bypassing the first {} features'.format(features_count))
        seperation_line()
        new_count = features_count
    if show:
        print(line)
    # when seeing seperation tag, increment count
    if '<<END>>' in line:
        if not show:
            features_count += 1
        # prompt human labeler for input for next feature entry
        if show:
            new_count += 1
            while True:
                print('\nEntry {}:'.format(new_count))
                print('Please apply a label to the above job posting')
                print('\n0: not interested, not qualified')
                print('1: interested, qualified')
                print('-1: quit labeling program')
                string_input = input('\nYour label: ')

                # validate user input
                try:
                    val = int(string_input.strip())
                except:
                    print('Error: value entered is not an integer')
                    continue
                if not val == 0 and not val == 1 and not val == -1:
                    print('Error: value entered is not a valid choice')
                    continue
                break
            # process user input
            if val == -1:
                print('\nExiting labeling program')
                seperation_line()
                break
            else:
                labels.write(str(val) + '\n')
                print('\nLabel {} applied'.format(val))
                seperation_line()

# close features and labels
features.close()
print('Closing', features_name)
labels.close()
print('Closing', labels_name)
