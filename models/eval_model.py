#!/usr/bin/env python3
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
Evaluate a predictive model using logistic regression with feature selection.

Usage: eval_model.py <csv_filename> [num_runs]

Read a training dataset from a CSV file and perform logistic regression with feature selection.
Evaluate the model's accuracy in predicting the output label and print the evaluation metrics.
"""

import os
import sys
import pandas as pd
import warnings
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import precision_score, recall_score, f1_score
from sklearn.model_selection import train_test_split
from sklearn.feature_selection import SequentialFeatureSelector
from tqdm import tqdm


def evaluate_predictive_model(csv_filename, num_runs=10):
    """Evaluate predictive model using logistic regression with feature selection."""
    # Load dataset from CSV file
    dataset = pd.read_csv(csv_filename)
    dataset = dataset.drop(columns=["ID","X","Y","Slice"])

    # Prepare input features and output label
    output_label = "class"
    _x = dataset.drop(output_label, axis=1)
    _y = dataset[output_label]

    # Create an empty DataFrame to store the results
    results_df = pd.DataFrame(
        columns=[
            "Selected Features",
            "Accuracy",
            "Precision",
            "Recall",
            "F1-score",
        ]
    )

    best_accuracy = 0.0
    best_feature_set = ""

    for i in tqdm(range(num_runs), unit="tests"):
        # Split dataset into training and testing sets
        _x_train, _x_test, _y_train, _y_test = train_test_split(
            _x, _y, test_size=0.5, random_state=None
        )

        # Use stepwise feature selection to find the best set of features
        logreg = LogisticRegression(solver="saga", max_iter=1000)
        sfs = SequentialFeatureSelector(logreg, n_features_to_select="auto")
        sfs.fit(_x_train, _y_train)
        _x_train_sfs = sfs.transform(_x_train)
        _x_test_sfs = sfs.transform(_x_test)

        # Train a logistic regression model with selected features
        logreg.fit(_x_train_sfs, _y_train)

        # Evaluate model's accuracy on the testing set
        accuracy = logreg.score(_x_test_sfs, _y_test)

        # Predict labels for the testing set
        y_pred = logreg.predict(_x_test_sfs)

        # Calculate precision, recall, and F1-score
        precision = precision_score(_y_test, y_pred, average="micro")
        recall = recall_score(_y_test, y_pred, average="micro")
        f1 = f1_score(_y_test, y_pred, average="micro")

        # Store the results in the DataFrame
        selected_features = ", ".join(_x.columns[sfs.get_support()])
        results_df.loc[i] = [
            selected_features,
            accuracy,
            precision,
            recall,
            f1,
        ]

        # Update the best feature set if the accuracy is higher
        if accuracy > best_accuracy:
            best_accuracy = accuracy
            best_feature_set = selected_features

    # Print the results
    print(f"Results [{csv_filename}]:")
    print(results_df.to_string())
    print("\nAverage:")
    print(results_df.iloc[:, 1:].mean().to_string())
    print("\nBest Feature Set:")
    print(f"{best_feature_set} @ {best_accuracy}")
    print(
        "--------------------------------------------------------------------------------------"
    )


if __name__ == "__main__":
    if len(sys.argv) > 1:
        if len(sys.argv) > 2:
            evaluate_predictive_model(sys.argv[1], int(sys.argv[2]))
        else:
            evaluate_predictive_model(sys.argv[1])
    else:
        print("Please provide the CSV filename as an argument.")
