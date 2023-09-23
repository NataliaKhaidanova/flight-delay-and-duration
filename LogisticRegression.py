from pyspark.ml.classification import LogisticRegression
from pyspark.ml.evaluation import MulticlassClassificationEvaluator, BinaryClassificationEvaluator
from utils import *

flights_train, flights_test = train_test_split()

# Create a classifier object and train on training data
logistic = LogisticRegression().fit(flights_train)

# Create predictions for the testing data and show confusion matrix
prediction = logistic.transform(flights_test)
prediction.groupBy('label', 'prediction').count().show()

# Calculate the elements of the confusion matrix
TN = prediction.filter('prediction = 0 AND label = prediction').count()
TP = prediction.filter('prediction = 1 AND label = prediction').count()
FN = prediction.filter('prediction = 0 AND label != prediction').count()
FP = prediction.filter('prediction = 1 AND label != prediction').count()

multi_evaluator = MulticlassClassificationEvaluator()
binary_evaluator = BinaryClassificationEvaluator()

accuracy = multi_evaluator.evaluate(prediction, {multi_evaluator.metricName: "accuracy"})
precision = TP / (TP + FP)
recall = TP / (TP + FN)
f1_score = 2 * (precision * recall) / (precision + recall)
auc = binary_evaluator.evaluate(prediction, {binary_evaluator.metricName: "areaUnderROC"})

print('''accuracy  = {:.2f}
precision = {:.2f}
recall    = {:.2f}
f1 score  = {:.2f}
AUC       = {:.2f}'''.format(accuracy, precision, recall, f1_score, auc))