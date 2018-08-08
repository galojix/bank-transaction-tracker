"""Module that uses machine learning techniques to categorise transactions."""
from nltk.stem.snowball import SnowballStemmer
from .database import db, Transaction, Category
from sklearn import model_selection
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_selection import SelectPercentile, f_classif
from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import accuracy_score
from sklearn.ensemble import AdaBoostClassifier
from sklearn import preprocessing
from sklearn import svm
# from time import time
import string


def collect_data():
    """Read transactions (descriptions and categories) from database.

    Add string of space separated stemmed words to feature_data list
    Add category to label_data list
    """
    feature_data = []
    label_data = []
    transactions = (
        db.session.query(Transaction, Category)
        .filter(Transaction.id == 1)
        .filter(Transaction.catno == Category.catno)
        .all())
    for transaction, category in transactions:
        description = stem_description(transaction.description)
        feature_data.append(description)
        label_data.append(transaction.catno)  # category.catname ?
    print("Amount of data: ", len(feature_data))
    return feature_data, label_data


def stem_description(description):
    """Stem the transaction description."""
    translator = str.maketrans('', '', string.punctuation)
    description = description.translate(translator)  # Remove punctuation
    stemmer = SnowballStemmer("english")
    description_list = description.split()
    stemmed_list = []
    for word in description_list:
        stemmed_list.append(stemmer.stem(word))
    stemmed_description = " ".join(stemmed_list)
    return stemmed_description


def split_data(feature_data, label_data):
    """Split data into train and test."""
    features_train, features_test, labels_train, labels_test = (
        model_selection.train_test_split(
            feature_data, label_data, test_size=0.1, random_state=42))
    return features_train, features_test, labels_train, labels_test


def vectorize_data(features_train, features_test):
    """Vectorize the feature data ie. create bag of words.

    Go from strings to lists of numbers
    (trans_no, word_no) freq_of_word_no
     vectorizer.get_feature_names()[word_no] is feature name

    """
    vectorizer = TfidfVectorizer(sublinear_tf=True, max_df=0.5,
                                 stop_words='english')
    features_train_transformed = vectorizer.fit_transform(features_train)
    features_test_transformed = vectorizer.transform(features_test)
    print('Number of features: ', len(vectorizer.get_feature_names()))
    return features_train_transformed, features_test_transformed


def feature_selection(features_train, features_test, labels_train):
    """Feature selection."""
    selector = SelectPercentile(f_classif, percentile=100)
    selector.fit(features_train, labels_train)
    features_train_transformed = selector.transform(features_train).toarray()
    features_test_transformed = selector.transform(features_test).toarray()
    return features_train_transformed, features_test_transformed


def naive_bayes(features_train, labels_train, features_test):
    """Naive Bayes."""
    clf = GaussianNB()
    # t0 = time()
    clf.fit(features_train, labels_train)
    # print("training time:", round(time() - t0, 3), "s")
    # t0 = time()
    predict = clf.predict(features_test)
    # print("predict time:", round(time() - t0, 3), "s")
    return predict


def adaboost(features_train, labels_train, features_test):
    """Adaboost algorithm."""
    clf = AdaBoostClassifier()
    # t0 = time()
    clf.fit(features_train, labels_train)
    # print("training time:", round(time() - t0, 3), "s")
    # t0 = time()
    predict = clf.predict(features_test)
    # print("predict time:", round(time() - t0, 3), "s")
    return predict


def svm_predict(features_train, labels_train, features_test):
    """SVM algorithm."""
    scaler = preprocessing.StandardScaler().fit(features_train)
    features_train = scaler.transform(features_train)
    features_test = scaler.transform(features_test)
    clf = svm.SVC()
    # t0 = time()
    clf.fit(features_train, labels_train)
    # print("training time:", round(time() - t0, 3), "s")
    # t0 = time()
    predict = clf.predict(features_test)
    # print("predict time:", round(time() - t0, 3), "s")
    return predict


def accuracy(labels_test, predict):
    """Accuracy."""
    score = accuracy_score(labels_test, predict)
    return score
