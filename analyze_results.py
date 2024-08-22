#!/usr/bin/python3
#
# This file is part of the DMI analysis scripts.
#
# Copyright (c) 2024 Jason Toney
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.

"""
    Erysiphe Necator DMI Fungicide Appressoria Assay
    ImageJ results analysis script

"""

import csv
import os
import sys
import pandas
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from sklearn.model_selection import train_test_split

# globals
REGR = ""


def setup_regression(model):
    """Setup the logistic regressions used to determine ROI identity."""
    # Replace with multinomial logistic regression
    # Use SAGA solver (??)
    dataset = pandas.read_csv(f"models/{model}_training_data.csv")
    _x = dataset.iloc[:, :-1]   # Features (all columns except the last one)
    _y = dataset.iloc[:, -1]    # Target variable (the last column)

    # split data into testing and training sets
    X_train, X_test, y_train, y_test = train_test_split(_x, _y, test_size=0.5, random_state=None)

    regression = LogisticRegression(multi_class="multinomial", solver="lbfgs", max_iter=1000)
    regression.fit(X_train, y_train)

    # make predictions on test data
    y_pred = regression.predict(X_test)

    # Eval the model
    print("Confusion Matrix:")
    print(confusion_matrix(y_test, y_pred))
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))
    print("\nAccuracy Score:")
    print(accuracy_score(y_test, y_pred))

    return regression


def analyze_results(folder):
    """A descriptive docstring belongs here."""
    results = [
        csv_handler(os.path.join(folder, csv_file))
        for csv_file in os.listdir(folder)
    ]
    print(results)


# handle csv datasets
def csv_handler(input_file):
    """Read CSV file produced by ImageJ and analyze each ROI using logistic regression."""
    image_data = 0
    # open csv file
    with open(
        input_file,
        "r",
        encoding="utf-8",
    ) as csv_file:
        # read csv as a dict so header is skipped and value lookup is simpler
        csv_reader = csv.DictReader(csv_file, delimiter=",")
        for row in csv_reader:
            image_data += 1
    return image_data


def main(folder):
    """Execute the main objective."""
    os.chdir(os.path.dirname(__file__))
    REGR = setup_regression("appressoria")
    analyze_results(folder)


if __name__ == "__main__":
    if len(sys.argv) == 2:
        main(sys.argv[1])
    else:
        sys.exit(f"Usage: {sys.argv[0]} [FOLDER]")
