import csv
import sys

from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier

TEST_SIZE = 0.4


def main():

    # Check command-line arguments
    if len(sys.argv) != 2:
        sys.exit("Usage: python shopping.py data")

    # Load data from spreadsheet and split into train and test sets
    evidence, labels = load_data(sys.argv[1])
    X_train, X_test, y_train, y_test = train_test_split(
        evidence, labels, test_size=TEST_SIZE
    )

    # Train model and make predictions
    model = train_model(X_train, y_train)
    predictions = model.predict(X_test)
    sensitivity, specificity = evaluate(y_test, predictions)

    # Print results
    print(f"Correct: {(y_test == predictions).sum()}")
    print(f"Incorrect: {(y_test != predictions).sum()}")
    print(f"True Positive Rate: {100 * sensitivity:.2f}%")
    print(f"True Negative Rate: {100 * specificity:.2f}%")


def load_data(filename):
    """
    Load shopping data from a CSV file `filename` and convert into a list of
    evidence lists and a list of labels. Return a tuple (evidence, labels).

    evidence should be a list of lists, where each list contains the
    following values, in order:
        - Administrative, an integer
        - Administrative_Duration, a floating point number
        - Informational, an integer
        - Informational_Duration, a floating point number
        - ProductRelated, an integer
        - ProductRelated_Duration, a floating point number
        - BounceRates, a floating point number
        - ExitRates, a floating point number
        - PageValues, a floating point number
        - SpecialDay, a floating point number
        - Month, an index from 0 (January) to 11 (December)
        - OperatingSystems, an integer
        - Browser, an integer
        - Region, an integer
        - TrafficType, an integer
        - VisitorType, an integer 0 (not returning) or 1 (returning)
        - Weekend, an integer 0 (if false) or 1 (if true)

    labels should be the corresponding list of labels, where each label
    is 1 if Revenue is true, and 0 otherwise.
    """
    evidence = list()
    labels = list()
    with open(filename, newline='\n') as shopping:
        shopping_reader = csv.reader(shopping, delimiter=',')
        for visitor in shopping_reader:
            if shopping_reader.line_num == 1:
                continue
            visitor_evidence = []
            # Administrative, an integer
            visitor_evidence.append(int(visitor[0])) 
            # Administrative_Duration, a floating point number
            visitor_evidence.append(float(visitor[1])) 
            # Informational, an integer
            visitor_evidence.append(int(visitor[2])) 
            # Informational_Duration, a floating point number
            visitor_evidence.append(float(visitor[3])) 
            # ProductRelated, an integer
            visitor_evidence.append(int(visitor[4])) 
            # ProductRelated_Duration, a floating point number
            visitor_evidence.append(float(visitor[5])) 
            # BounceRates, a floating point number
            visitor_evidence.append(float(visitor[6])) 
            # ExitRates, a floating point number
            visitor_evidence.append(float(visitor[7])) 
            # PageValues, a floating point number
            visitor_evidence.append(float(visitor[8])) 
            # SpecialDay, a floating point number
            visitor_evidence.append(float(visitor[9]))
            # Dict of month numbers
            MONTHS = {"Jan": 0, "Feb": 1, "Mar": 2,
                    "Apr": 3, "May": 4, "Jun": 5, "June": 5,
                    "Jul": 6, "Aug": 7, "Sep": 8, "Oct": 9,
                    "Nov": 10, "Dec": 11}
            # Month, an index from 0 (January) to 11 (December)
            visitor_evidence.append(MONTHS[visitor[10]])
            # OperatingSystems, an integer
            visitor_evidence.append(int(visitor[11]))
            # Browser, an integer
            visitor_evidence.append(int(visitor[12]))
            # Region, an integer
            visitor_evidence.append(int(visitor[13]))
            # TrafficType, an integer
            visitor_evidence.append(int(visitor[14]))
            # VisitorType, an integer 0 (not returning) or 1 (returning)
            visitor_evidence.append(int(visitor[15] == "Returning_Visitor"))
            # Weekend, an integer 0 (if false) or 1 (if true)
            visitor_evidence.append(int(visitor[16] == "TRUE"))

            # all csv values except revenue, formatted 
            evidence.append(visitor_evidence) 
            # 1 if Revenue is true, and 0 otherwise
            labels.append(int(visitor[17] == "TRUE"))

    shopping.close()
    return (evidence, labels)
            

def train_model(evidence, labels):
    """
    Given a list of evidence lists and a list of labels, return a
    fitted k-nearest neighbor model (k=1) trained on the data.
    """
    model = KNeighborsClassifier(n_neighbors=1)
    model.fit(evidence, labels)
    return model


def evaluate(labels, predictions):
    """
    Given a list of actual labels and a list of predicted labels,
    return a tuple (sensitivity, specificty).

    Assume each label is either a 1 (positive) or 0 (negative).

    `sensitivity` should be a floating-point value from 0 to 1
    representing the "true positive rate": the proportion of
    actual positive labels that were accurately identified.

    `specificity` should be a floating-point value from 0 to 1
    representing the "true negative rate": the proportion of
    actual negative labels that were accurately identified.
    """
    postitive_labels = 0
    positive_labels_accurately_identified = 0
    negative_labels = 0
    negative_labels_accurately_identified = 0
    for label, prediction in zip(labels, predictions):
        if label == True:
            postitive_labels += 1
            if label == prediction:
                positive_labels_accurately_identified += 1
        if label == False:
            negative_labels += 1
            if label == prediction:
                negative_labels_accurately_identified += 1
    sensitivity = positive_labels_accurately_identified / postitive_labels
    specificity = negative_labels_accurately_identified / negative_labels
    return (sensitivity, specificity)


if __name__ == "__main__":
    main()
