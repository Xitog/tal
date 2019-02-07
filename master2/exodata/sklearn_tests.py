#-----------------------------------------------------------
# Import
#-----------------------------------------------------------

# Standard library
import datetime
import pickle

# External Library
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn import tree
from sklearn.metrics import confusion_matrix
import numpy as np
from sklearn import svm
#from sklearn.preprocessing import LabelEncoder
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import FeatureUnion
from sklearn.preprocessing import OneHotEncoder
from sklearn import svm

# Project Library
from preprocess import MiniTitle, read_base_csv, write_to_csv

#-----------------------------------------------------------
# Switch
#-----------------------------------------------------------

# To convert data
CONVERT_PICKLE_TO_CSV = False               # Take the two bin and make a CSV. Used for making a CSV with Silhouette instead of titles
CONVERT_CSV = False
CONVERT_INPUT = "data/litl-exam.csv"        # 3000 10000 20000 rien
CONVERT_OUTPUT = "data/sharp53426.csv"      # 3000 10000 20000 53426

# Target of predicting
DATA_INPUT = "data/sharp53426.csv"     # 3000 10000 20000 53426 (=titles) 53426silhouette (=only sil)

# To predict on only title or silhouette change DATA_INPUT
DECISION_TREE_PREDICT = False
DECISION_TREE_EXPORT_DOT = False
DECISION_TREE_PRINT_CODE = False # must be done with debug. To big :-(
DECISION_TREE_ERROR_DISPLAY = False

# To predict with SVM on only title or silhouette (change DATA_INPUT to choose)
SVM_PREDICT = False # PREDICT, TRUE_GRID and FALSE_GRID ARE EXCLUSIVE
SVM_PREDICT_C = 1000. # C value, default 100.
SVM_TRUE_GRID = False
SVM_FALSE_GRID = False # house made multitest
SVM_ERROR_DISPLAY = False # option for SVM_PREDICT only

# To predict on all features
DECISION_PREDICT_ALL = True
SVM_PREDICT_ALL = False

#-----------------------------------------------------------
# Convert data
#-----------------------------------------------------------

def pickle2csv():
    print('Loading Train Corpus from pickle')
    train = pickle.load(open('data/train.bin', mode='rb'))
    print('Loading Test Corpus from pickle')
    test = pickle.load(open('data/test.bin', mode='rb'))
    lines = []
    lines.append("Domaine###Support###Année###Nauteurs###Titre")
    for t in train:
        lines.append(t.domain + "###" + t.support + "###" + str(t.year) + "###" + str(t.authors) + "###" + " ".join(t.filtered))
    for t in test:
        lines.append(t.domain + "###" + t.support + "###" + str(t.year) + "###" + str(t.authors) + "###" + " ".join(t.filtered))
    f = open("data/sharp53426silhouette.csv", mode="w", encoding="utf8")
    for lin in lines:
        f.write(lin + "\n")
    f.close()
    del train
    del test

if CONVERT_PICKLE_TO_CSV:
    pickle2csv()

def make_panda(filepath):
    """From CSV to Panda"""
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
    del lines

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

class TextSelector(BaseEstimator, TransformerMixin):
    """
    Transformer to select a single column from the data frame to perform additional transformations on
    Use on text columns in the data
    """
    def __init__(self, key):
        self.key = key

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        return X[self.key].values.astype('U')
    
class NumberSelector(BaseEstimator, TransformerMixin):
    """
    Transformer to select a single column from the data frame to perform additional transformations on
    Use on numeric columns in the data
    """
    def __init__(self, key):
        self.key = key

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        return X[[self.key]].values.astype('float64')

def all_feature(Xtrain, Ytrain, Xtest, Ytest):
    # make the pipeline
    text = Pipeline([
                ('selector', TextSelector(key='Titre')),
                ('tfidf', TfidfVectorizer())
            ])
    text.fit_transform(Xtrain)
    year = Pipeline([
                ('selector', NumberSelector(key='Année'))
                #('standard', StandardScaler())
            ])
    year.fit_transform(Xtrain)
    authors = Pipeline([
                ('selector', NumberSelector(key='Nauteurs'))
                #('standard', StandardScaler())
            ])
    authors.fit_transform(Xtrain)
    support_COMM = Pipeline([
                ('selector', NumberSelector(key='support_COMM'))
                #('standard', StandardScaler())
            ])
    support_COMM.fit_transform(Xtrain)
    support_COUV = Pipeline([
                ('selector', NumberSelector(key='support_COUV'))
                #('standard', StandardScaler())
            ])
    support_COUV.fit_transform(Xtrain)
    support_ART = Pipeline([
                ('selector', NumberSelector(key='support_ART'))
                #('standard', StandardScaler())
            ])
    support_ART.fit_transform(Xtrain)
    #support = Pipeline([
    #            ('selector', TextSelector(key='Support')),
    #            ('ohe', OneHotEncoder(dtype=int, sparse=False))
    #        ])
    #support.fit_transform(Xtrain)
    # merge all the feature
    feats = FeatureUnion([('text', text), 
                          ('year', year),
                          ('authors', authors),
                          #('support', support)
                          ('support_COMM', support_COMM),
                          ('support_COUV', support_COUV),
                          ('support_ART', support_ART),
                        ])
    feature_processing = Pipeline([('feats', feats)])
    feature_processing.fit_transform(Xtrain)
    # add a classifier
    if DECISION_PREDICT_ALL:
        pipeline = Pipeline([
            ('features',feats),
            ('classifier', tree.DecisionTreeClassifier(min_samples_split=20, random_state=99)),
        ])
    elif SVM_PREDICT_ALL:
        pipeline = Pipeline([
            ('features',feats),
            ('classifier', svm.SVC(gamma=0.001, C=100.)),
        ])
    start_time = datetime.datetime.now()
    pipeline.fit(Xtrain, Ytrain)
    print('Fit Duration : ' + str(datetime.datetime.now() - start_time))
    start_time = datetime.datetime.now()
    res = pipeline.predict(Xtest)
    print('Predict Duration : ' + str(datetime.datetime.now() - start_time))
    acc = pipeline.score(Xtest, Ytest)
    print("Confusion matrix")
    print(confusion_matrix(Ytest, res))
    print("Accuracy =", acc)
    
    #le = LabelEncoder()
    #data['Support'] = le.fit_transform(data['Support'])

if DECISION_PREDICT_ALL or SVM_PREDICT_ALL:
    data = make_panda(DATA_INPUT)
    Xtrain, Xtest = make_train_test(data)
    Ytrain = Xtrain["Domaine"]
    Xtrain = Xtrain.drop('Domaine', axis=1)
    Xtrain = pd.get_dummies(Xtrain, prefix='support', dtype=int, columns=['Support'])
    Ytest = Xtest["Domaine"]
    Xtest = Xtest.drop('Domaine', axis=1)
    Xtest = pd.get_dummies(Xtest, prefix='support', dtype=int, columns=['Support'])
    all_feature(Xtrain, Ytrain, Xtest, Ytest)

def make_model(data, filename, debug=False, export=False):
    vec = TfidfVectorizer()
    try:
        X = vec.fit_transform(data["Titre"])
    except ValueError:
        X = vec.fit_transform(data['Titre'].values.astype('U'))
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
    try:
        Xtest = vec.transform(data["Titre"])
    except ValueError:
        Xtest = vec.transform(data["Titre"].values.astype('U'))
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

    f = open('code.txt', mode='w', encoding='utf8')
    def recurse(left, right, threshold, features, node, depth, max_depth=None, f=None):
        spacer = spacer_base * depth
        if (threshold[node] != -2):
            print(spacer + "if ( " + features[node] + " <= " + \
                  str(threshold[node]) + " ) {", file=f)
            if left[node] != -1:
                if max_depth is None or depth+1 < max_depth:
                    recurse(left, right, threshold, features,
                            left[node], depth+1, max_depth, f)
            print(spacer + "}\n" + spacer +"else {", file=f)
            if right[node] != -1:
                if max_depth is None or depth+1 < max_depth:
                    recurse(left, right, threshold, features,
                        right[node], depth+1, max_depth, f)
            print(spacer + "}", file=f)
        else:
            target = value[node]
            for i, v in zip(np.nonzero(target)[1],
                            target[np.nonzero(target)]):
                target_name = target_names[i]
                target_count = int(v)
                print(spacer + "return " + str(target_name) + \
                      " ( " + str(target_count) + " examples )", file=f)

    recurse(left, right, threshold, features, 0, 0, max_depth)
    f.close()

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
    data = make_panda(DATA_INPUT)
    train, test = make_train_test(data)
    vec, dt, ohe, trainTransformed = make_model(data, DATA_INPUT.replace('.csv', '.dot'), debug=DECISION_TREE_PRINT_CODE, export=DECISION_TREE_EXPORT_DOT)
    print("Dimension of =", repr(trainTransformed))
    print('Node count =', dt.tree_.node_count)
    print('Max depth of tree=', dt.tree_.max_depth)
    if DECISION_TREE_PRINT_CODE: # with debug !
        get_code(dt, ohe.columns, data["Domaine"].unique(), "  ", 20)
    start_time = datetime.datetime.now()
    res, acc = predict(vec, dt, test)
    print('Predict Duration : ' + str(datetime.datetime.now() - start_time))
    if DECISION_TREE_ERROR_DISPLAY:
        #get_errors(data, res, trainTransformed, 10)
        f = open('all_errors_decision_tree.txt', mode='w', encoding='utf8')
        for i in range(0, len(test["Domaine"])):
            ground_truth = test["Domaine"].iloc[i]
            if res[i] != ground_truth:
                print('?=', f"{res[i]:12}", '=', f"{ground_truth:12}", test.iloc[i]["Titre"], file=f)
        f.close()

#-----------------------------------------------------------
# SVM
#-----------------------------------------------------------

def fit_predict(clf, XtrainVec, Ytrain, XtestVec, Ytest):
    start_time = datetime.datetime.now()
    clf.fit(XtrainVec, Ytrain)
    print('Fit Duration : ' + str(datetime.datetime.now() - start_time))
    start_time = datetime.datetime.now()
    res = clf.predict(XtestVec)
    print('Predict Duration : ' + str(datetime.datetime.now() - start_time))
    acc = clf.score(XtestVec, Ytest)
    print("Confusion matrix")
    print(confusion_matrix(Ytest, res))
    print("Accuracy =", acc)
    if isinstance(clf, svm.SVC):
        print("Kernel =", clf.kernel)
        print("Info on classifier SVM =\n", clf)
    else:
        print("Info on best_estimator_ =\n", clf.best_estimator_)
    return res
        
if SVM_PREDICT or SVM_TRUE_GRID or SVM_FALSE_GRID:
    print('SVM Predict on', DATA_INPUT)
    data = make_panda(DATA_INPUT)
    Xtrain, Xtest = make_train_test(data)
    Ytrain = Xtrain["Domaine"]
    Xtrain = Xtrain.drop('Domaine', axis=1)
    Xtrain = Xtrain.drop('Support', axis=1)
    Xtrain = Xtrain.drop('Année', axis=1)
    Xtrain = Xtrain.drop('Nauteurs', axis=1)
    
    Ytest = Xtest["Domaine"]
    Xtest = Xtest.drop('Domaine', axis=1)
    Xtest = Xtest.drop('Support', axis=1)
    Xtest = Xtest.drop('Année', axis=1)
    Xtest = Xtest.drop('Nauteurs', axis=1)

    vec = TfidfVectorizer()
    try:
        XtrainVec = vec.fit_transform(Xtrain['Titre'])
    except ValueError:
        XtrainVec = vec.fit_transform(Xtrain['Titre'].values.astype('U'))
    try:
        XtestVec = vec.transform(Xtest["Titre"])
    except ValueError:
        XtestVec = vec.transform(Xtest["Titre"].values.astype('U'))

    if SVM_TRUE_GRID:
        print("True Grid")
        from sklearn.model_selection import GridSearchCV
        param_grid = [
            #{ 'kernel' : ['linear'], 'C' : [10., 100., 1000.] },
            #OK { 'kernel' : ['rbf'], 'gamma' : [0.001, 0.0001], 'C' : [100., 1000.] },
            #OK { 'kernel' : ['linear'], 'gamma' : [0.001], 'C' : [1000.] },
            { 'kernel' : ['rbf'], 'gamma' : [0.0001], 'C' : [100.] },
            #{ 'kernel' : ['linear'], 'C' : [1., 10., 100., 1000.] },
            #{ 'kernel' : ['rbf'], 'gamma' : [0.001, 0.0001], 'C' : [1., 10., 100., 1000.] },
            #{ 'kernel' : ['poly'], 'gamma' : [0.001, 0.0001],'degree' : [2, 3], 'C' : [1., 10., 100., 1000.] },
        ]
        print(param_grid)
        clf = GridSearchCV(svm.SVC(), param_grid, cv=2)
        fit_predict(clf, XtrainVec, Ytrain, XtestVec, Ytest)
    if SVM_FALSE_GRID:
        print("False Grid")
        print('Kernel =    rbf, C =  100 ==========================================')
        clf = svm.SVC(kernel='rbf', gamma=0.001, C=100.)
        fit_predict(clf, XtrainVec, Ytrain, XtestVec, Ytest)
        print('Kernel =    rbf, C =   10 ==========================================')
        clf = svm.SVC(kernel='rbf', gamma=0.001, C=10.)
        fit_predict(clf, XtrainVec, Ytrain, XtestVec, Ytest)
        print('Kernel =    rbf, C = 1000 ==========================================')
        clf = svm.SVC(kernel='rbf', gamma=0.001, C=1000.)
        fit_predict(clf, XtrainVec, Ytrain, XtestVec, Ytest)
        print('Kerbel = linear, C = 100 ==========================================')
        clf = svm.SVC(kernel='linear', C=1000.)
        fit_predict(clf, XtrainVec, Ytrain, XtestVec, Ytest)
    if SVM_PREDICT:
        print("Normal One SVM")
        clf = svm.SVC(kernel='rbf', gamma=0.001, C=SVM_PREDICT_C)
        res = fit_predict(clf, XtrainVec, Ytrain, XtestVec, Ytest)
        if SVM_ERROR_DISPLAY:
            f = open('all_errors_svm_sil_C100.txt', mode='w', encoding='utf8')
            for i in range(0, len(Ytest)):
                if res[i] != Ytest.iloc[i]:
                    print('?=', f"{res[i]:12}", '=', f"{Ytest.iloc[i]:12}", Xtest.iloc[i]["Titre"], file=f)
            f.close()



