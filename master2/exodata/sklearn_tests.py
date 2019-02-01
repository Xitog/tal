#-----------------------------------------------------------
# Import
#-----------------------------------------------------------

# Standard library
import datetime

# External Library
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn import tree
from sklearn.metrics import confusion_matrix
import numpy as np
from sklearn import svm

# Project Library
from preprocess import read_base_csv, write_to_csv

CONVERT_CSV = False
CONVERT_INPUT = "data/litl-exam-20000.csv" # 3000 10000 20000 rien
CONVERT_OUTPUT = "data/sharp20000.csv"     # 3000 10000 20000 53426
PREDICT_INPUT = "data/sharp53426.csv"      # 3000 10000 20000 53426
DECISION_TREE_PREDICT = True
SVM_PREDICT = True

#-----------------------------------------------------------
# Convert data
#-----------------------------------------------------------

def make_panda(filepath):
    print("Information on the dataframe\n---")
    data = pd.read_csv(filepath, sep="###", engine='python', encoding='utf8')
    print(data.dtypes)
    print(data.describe())
    data.head(5)
    print(data.columns)
    return data

if CONVERT_CSV:
    lines = read_base_csv(CONVERT_INPUT)
    write_to_csv(CONVERT_OUTPUT, lines)
    print()

#-----------------------------------------------------------
# Prepare data
#-----------------------------------------------------------

def make_train_test(data):
    tiers = int(len(data)/3)
    train, test = train_test_split(data,
                               train_size = len(data) - tiers, #35_618
                               test_size = tiers,
                               random_state=1,
                               stratify=data["Domaine"])
    print("\nCompare the frequence of domains in both set\n---")
    freqTrain = pd.crosstab(index=train["Domaine"], columns="count")
    print(freqTrain/freqTrain.sum())
    freqTest = pd.crosstab(index=test["Domaine"], columns="count")
    print(freqTest/freqTest.sum())
    return train, test

#-----------------------------------------------------------
# Decision Tree
#-----------------------------------------------------------

def make_model(data, filename, debug=False, export=False):
    vec = TfidfVectorizer()
    X = vec.fit_transform(data["Titre"])
    if debug:
        ohe = pd.DataFrame(X.toarray(), columns=vec.get_feature_names())
        print(ohe)
    dt = tree.DecisionTreeClassifier(min_samples_split=20, random_state=99)
    dt.fit(X, data["Domaine"]) # feature, target
    if export == True:
        f = open(filename, "w", encoding='utf8')
        tree.export_graphviz(dt, out_file=f, feature_names=vec.get_feature_names(),
                         class_names=data["Domaine"].unique(),
                         filled=True, rounded=True,  
                         special_characters=True)
        f.close()
    if debug:
        return vec, dt, ohe, X
    else:
        return vec, dt, None, X


def predict(vec, model, data):
    Xtest = vec.transform(data["Titre"])
    # 8709 (train) vs 6646 (test)
    res = model.predict(Xtest)
    acc = model.score(Xtest, data["Domaine"])
    print("Confusion matrix")
    print(confusion_matrix(data["Domaine"], res))
    print("Accuracy =", acc)
    return res, acc


def get_code(tree, feature_names, target_names,
             spacer_base="    ", max_depth = None):
    left      = tree.tree_.children_left
    right     = tree.tree_.children_right
    threshold = tree.tree_.threshold
    features  = [feature_names[i] for i in tree.tree_.feature]
    value = tree.tree_.value

    def recurse(left, right, threshold, features, node, depth, max_depth=None):
        spacer = spacer_base * depth
        if (threshold[node] != -2):
            print(spacer + "if ( " + features[node] + " <= " + \
                  str(threshold[node]) + " ) {")
            if left[node] != -1:
                if max_depth is None or depth+1 < max_depth:
                    recurse(left, right, threshold, features,
                            left[node], depth+1, max_depth)
            print(spacer + "}\n" + spacer +"else {")
            if right[node] != -1:
                if max_depth is None or depth+1 < max_depth:
                    recurse(left, right, threshold, features,
                        right[node], depth+1, max_depth)
            print(spacer + "}")
        else:
            target = value[node]
            for i, v in zip(np.nonzero(target)[1],
                            target[np.nonzero(target)]):
                target_name = target_names[i]
                target_count = int(v)
                print(spacer + "return " + str(target_name) + \
                      " ( " + str(target_count) + " examples )")

    recurse(left, right, threshold, features, 0, 0, max_depth)

# dataTransformed not yet used
def get_errors(data, predicted, dataTransformed, nb = 2):
    print("\nErrors\n---\n")
    # domain has an header line!
    for i in range(0, len(predicted)):
        if data["Domaine"][i+1] != predicted[i]:
            print(f'GroundTruth = {data["Domaine"][i+1]:10} vs Predicted = {predicted[i]:10}')
            print('Titre =', data["Titre"][i+1])
            print(data.iloc[i+1])
            print(dataTransformed[i])
            print()
            nb -= 1
        if nb == 0: break


if DECISION_TREE_PREDICT:
    data = make_panda(PREDICT_INPUT)
    train, test = make_train_test(data)
    vec, dt, ohe, trainTransformed = make_model(data, PREDICT_INPUT.replace('.csv', '.dot'))
    print("Dimension of =", repr(trainTransformed))
    print('Node count =', dt.tree_.node_count)
    print('Max depth of tree=', dt.tree_.max_depth)
    #get_code(dt, ohe.columns, data["Domaine"].unique(), "  ", 20)
    start_time = datetime.datetime.now()
    res, acc = predict(vec, dt, test)
    print('Duration : ' + str(datetime.datetime.now() - start_time))
    get_errors(data, res, trainTransformed, 10)

#-----------------------------------------------------------
# SVM
#-----------------------------------------------------------

#clf = svm.SVC(gamma=0.001, C=100.)
#clf.fit(digits.data[:-1], digits.target[:-1])  # feature = all colums but last, target = last column***
#clf.predict(digits.data[-1:])

