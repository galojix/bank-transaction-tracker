"""Module that uses machine learning techniques to categorise transactions."""

# Collect data from database
#
# Read transactions (descriptions and categories) from database
# For each description:
#     Add string of space separated stemmed words to feature_data list
#     Add category to label_data list

# Split data into Train and Test
#
# from sklearn import cross_validation
# features_train, features_test, labels_train, labels_test
#     = cross_validation.train_test_split(feature_data, label_data,
#                                         test_size=0.1, random_state=42)

# Vectorize the feature data ie. create bag of words
#
# Go from strings to lists of numbers
# TfIdf vectorize feature_data list into bag of words:
#     (trans_no, word_no) freq_of_word_no
#     vectorizer.get_feature_names()[word_no] is feature name
# from sklearn.feature_extraction.text import TfidfVectorizer
# vectorizer = TfidfVectorizer(sublinear_tf=True, max_df=0.5,
#                              stop_words='english')
# features_train_transformed = vectorizer.fit_transform(features_train)
# features_test_transformed  = vectorizer.transform(features_test)


# Feature Selection
# from sklearn.feature_selection import SelectPercentile, f_classif
# selector = SelectPercentile(f_classif, percentile=10)
# selector.fit(features_train_transformed, labels_train)
# features_train_transformed = selector.transform(
#     features_train_transformed).toarray()
# features_test_transformed  = selector.transform(
#    features_test_transformed).toarray()
# Now have:
# features_train_transformed, features_test_transformed,
# labels_train,labels_test

# Algorithms/Classifiers
#
# Try Naive Bayes and Adaboost
#
# from sklearn.naive_bayes import GaussianNB
# clf = GaussianNB()
# t0 = time()
# clf.fit(features_train, labels_train)
# print "training time:", round(time()- t0, 3), "s"
# t0 = time()
# predict = clf.predict(features_test)
# print "predict time:", round(time()- t0, 3), "s"
#
# from sklearn.ensemble import AdaBoostClassifier
# from time import time
# clf = AdaBoostClassifier()
# print('Fitting:')
# start_time = time()
# clf.fit(features_train, labels_train)
# duration = time() - start_time
# print('Training time:', duration)
# print('Predicting:')
# start_time = time()
# predict = clf.predict(features_test)
# duration = time() - start_time
# print('Prediction time:', duration)

# Evaluation of classifiers
#
# from sklearn.metrics import accuracy_score
# accuracy = accuracy_score(labels_test, predict)
# print(accuracy)
#
# from sklearn.metrics import accuracy_score
# accuracy = accuracy_score(labels_test, predict)
# print('Accuracy:', accuracy)
#
# from sklearn.metrics import accuracy_score
# accuracy = accuracy_score(labels_test, predict)
# results = zip(labels_test, predict)
# print(results)
# true_positives = 0
# false_negatives = 0
# false_positives = 0
# for result in results:
#     if result[0] == 1.0 and result[1] == 1.0:  # true positive
#         true_positives += 1
#     if result[0] == 1.0 and result[1] == 0.0:  # false negative
#         false_negatives += 1
#     if result[0] == 0.0 and result[1] == 1.0:  # false positive
#         false_positives += 1
# recall = float(true_positives) / (true_positives + false_negatives)
# precision = float(true_positives) / (true_positives + false_positives)
# print('Recall: ', recall)
# print('Precision: ', precision)
