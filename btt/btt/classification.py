"""Module that uses machine learning techniques to categorise transactions."""
from nltk.stem.snowball import SnowballStemmer
from .database import db, Transaction, Category
from sklearn import model_selection
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_selection import SelectPercentile, f_classif
from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import accuracy_score
from sklearn import preprocessing
from sklearn import svm
from flask_login import current_user
from flask import session
from dateutil.parser import parse
import string


def classification_score(group_id):
    """Calculate transaction classification score for group.

    This is used for checking algorithm from command line.
    """
    feature_data, label_data = collect_data_for_group(group_id)
    data_size = len(feature_data)
    features_train, features_test, labels_train, labels_test = split_data(
        feature_data, label_data
    )
    features_train, features_test, num_features = vectorize_data(
        features_train, features_test
    )
    features_train, features_test = feature_selection(
        features_train, features_test, labels_train
    )
    predict = svm_predict(features_train, labels_train, features_test)
    score = accuracy_score(labels_test, predict)
    return score, data_size, num_features


def predict_categories():
    """Predict transaction categories."""
    features_train, labels_train = collect_data()
    features_test = get_test_features()
    if len(features_train) == 0:
        predict = ["Unspecified Expense" for _ in features_test]
        return predict
    features_train, features_test, num_features = vectorize_data(
        features_train, features_test
    )
    features_train, features_test = feature_selection(
        features_train, features_test, labels_train
    )
    predict = svm_predict(features_train, labels_train, features_test)
    return predict


def predict_columns():
    """Predict transaction column labels."""
    transactions = session["uploaded_transactions"]
    result = ["ignore" for _ in range(len(transactions[0]))]
    header_row = False
    for i, value in enumerate(transactions[0]):
        if "date" in value.lower():
            result[i] = "date"
            header_row = True
        elif "description" in value.lower() or "narration" in value.lower():
            result[i] = "description"
            header_row = True
        elif (
            "dr" in value.lower() and "cr" in value.lower() and len(value) < 6
        ):
            result[i] = "drcr"
            header_row = True
        elif "debit" in value.lower():
            result[i] = "dr"
            header_row = True
        elif "dr" in value.lower() and len(value) < 5:
            result[i] = "dr"
            header_row = True
        elif "credit" in value.lower():
            result[i] = "cr"
            header_row = True
        elif "cr" in value.lower() and len(value) < 5:
            result[i] = "cr"
            header_row = True
    if not header_row:
        for i, value in enumerate(transactions[1]):
            if is_number(value):
                result[i] = "drcr"
            elif is_date(value):
                result[i] = "date"
            elif len(value) > 10:
                result[i] = "description"
    return result, header_row


def is_date(string):
    """Is string a date."""
    try:
        parse(string)
        return True
    except ValueError:
        return False


def is_number(s):
    """Is string a number."""
    try:
        float(s)
        return True
    except ValueError:
        return False


def collect_data():
    """Get existing transaction descriptions and categories."""
    feature_data = []
    label_data = []
    transactions = current_user.group().transactions
    for transaction in transactions:
        description = stem_description(transaction.description)
        feature_data.append(description)
        label_data.append(transaction.category.catname)
    # print('*******************************************************')
    # for num, feature in enumerate(feature_data):
    #     if 'myer' in feature:
    #         print(feature, label_data[num])
    # print('*******************************************************')
    return feature_data, label_data


def get_test_features():
    """Get test features from uploaded transactions."""
    features_test = []
    transactions = session["uploaded_transactions"]
    for transaction in transactions:
        description = " ".join(transaction)
        description = stem_description(description)
        features_test.append(description)
    # print('*******************************************************')
    # for num, feature in enumerate(features_test):
    #     if 'myer' in feature:
    #         print(num, ':', feature)
    # print('*******************************************************')
    return features_test


def collect_data_for_group(group_id):
    """Read transactions (descriptions and categories) from database.

    Add string of space separated stemmed words to feature_data list
    Add category to label_data list
    """
    feature_data = []
    label_data = []
    transactions = (
        db.session.query(Transaction, Category)
        .filter(Transaction.group_id == group_id)
        .filter(Transaction.catno == Category.catno)
        .all()
    )
    for transaction, category in transactions:
        description = stem_description(transaction.description)
        feature_data.append(description)
        label_data.append(category.catname)
    return feature_data, label_data


def stem_description(description):
    """Stem the transaction description."""
    translator = str.maketrans("", "", string.punctuation)
    description = description.translate(translator)  # Remove punctuation
    stemmer = SnowballStemmer("english")
    description_list = description.split()
    stemmed_list = [stemmer.stem(word) for word in description_list]
    return " ".join(stemmed_list)


def split_data(feature_data, label_data):
    """Split data into train and test."""
    (
        features_train,
        features_test,
        labels_train,
        labels_test,
    ) = model_selection.train_test_split(
        feature_data, label_data, test_size=0.1, random_state=42
    )
    return features_train, features_test, labels_train, labels_test


def vectorize_data(features_train, features_test):
    """Vectorize the feature data ie. create bag of words.

    Go from strings to lists of numbers
    (trans_no, word_no) freq_of_word_no
     vectorizer.get_feature_names()[word_no] is feature name

    """
    vectorizer = TfidfVectorizer(
        sublinear_tf=True, max_df=0.5, stop_words="english"
    )
    features_train_transformed = vectorizer.fit_transform(features_train)
    features_test_transformed = vectorizer.transform(features_test)
    num_features = len(vectorizer.get_feature_names())
    return features_train_transformed, features_test_transformed, num_features


def feature_selection(features_train, features_test, labels_train):
    """Feature selection."""
    selector = SelectPercentile(f_classif, percentile=100)
    selector.fit(features_train, labels_train)
    features_train_transformed = selector.transform(features_train).toarray()
    features_test_transformed = selector.transform(features_test).toarray()
    return features_train_transformed, features_test_transformed


def naive_bayes_predict(features_train, labels_train, features_test):
    """Naive Bayes."""
    clf = GaussianNB()
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
