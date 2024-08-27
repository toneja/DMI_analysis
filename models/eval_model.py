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
from sklearn.feature_selection import SelectKBest, mutual_info_classif
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"
from tensorflow.keras.layers import Dense, Input
from tensorflow.keras.models import Sequential
from tensorflow.keras.utils import to_categorical


def evaluate_predictive_model(csv_filename):
    """Evaluate predictive model using logistic regression with feature selection."""
    # Load dataset from CSV file
    dataset = pd.read_csv(csv_filename)
    dataset = dataset.drop(columns=["ID","X","Y","Slice"])

    # Prepare input features and output label
    output_label = "class"
    _x = dataset.drop(output_label, axis=1)
    _y = dataset[output_label]

    # Convert string labels to integer labels
    label_encoder = LabelEncoder()
    _y = label_encoder.fit_transform(_y)

    # Feature selection
    _k = 10  # Select top 10 features
    selector = SelectKBest(score_func=mutual_info_classif, k=_k)
    _x_selected = selector.fit_transform(_x, _y)
    selected_features = dataset.columns[selector.get_support(indices=True)]
    print(f"Selected Features: {selected_features}")

    # Convert the target variable to categorical (one-hot encoding)
    # Necessary for neural network to handle multiple classes
    _y = to_categorical(_y)

    # Split dataset into training and testing sets
    _x_train, _x_test, _y_train, _y_test = train_test_split(
        _x_selected, _y, test_size=0.3, random_state=None
    )

    # Build the neural network model
    model = Sequential()
    model.add(Input(shape=(_x_train.shape[1],)))
    model.add(Dense(64, activation="relu"))
    model.add(Dense(32, activation="relu"))
    model.add(Dense(_y.shape[1], activation="softmax"))

    # Compile the model
    model.compile(optimizer="adam", loss="categorical_crossentropy", metrics=["accuracy"])

    # Train the model
    model.fit(_x_train, _y_train, epochs=100, batch_size=10, verbose=1)

    # Eval the model
    _y_pred = model.predict(_x_test, verbose=0)
    _y_pred_classes = _y_pred.argmax(axis=1)
    _y_test_classes = _y_test.argmax(axis=1)

    # Print the eval metrics
    print("Confusion Matrix:")
    print(confusion_matrix(_y_test_classes, _y_pred_classes))
    print("\nClassification Report:")
    print(classification_report(_y_test_classes, _y_pred_classes))
    print("\nAccuracy Score:")
    print(accuracy_score(_y_test_classes, _y_pred_classes))


if __name__ == "__main__":
    if len(sys.argv) > 1:
        evaluate_predictive_model(sys.argv[1])
    else:
        print("Please provide the CSV filename as an argument.")
