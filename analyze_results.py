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
import numpy as np
import pandas
from sklearn.preprocessing import LabelEncoder
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"
from tensorflow.keras.layers import Dense, Input
from tensorflow.keras.models import Sequential
from tensorflow.keras.utils import to_categorical
from tabulate import tabulate

# globals
NNET = ""


def setup_neural_network():
    """Setup the neural network used to determine ROI identity."""
    dataset = pandas.read_csv(f"models/appressoria_training_data.csv")
    _x = dataset[
        [
            "Area",
            "Perim.",
            "Major",
            "Minor",
            "Circ.",
            "Feret",
            "MinFeret",
            "AR",
            "Round",
            "Solidity",
        ]
    ]
    _y = dataset["class"]
    # Convert string labels to integer labels
    label_encoder = LabelEncoder()
    _y = label_encoder.fit_transform(_y)
    # Convert the target variable to categorical (one-hot encoding)
    # Necessary for neural network to handle multiple classes
    _y = to_categorical(_y)
    model = Sequential()
    model.add(Input(shape=(_x.shape[1],)))
    model.add(Dense(64, activation="relu"))
    model.add(Dense(32, activation="relu"))
    model.add(Dense(_y.shape[1], activation="softmax"))
    model.compile(
        optimizer="adam", loss="categorical_crossentropy", metrics=["accuracy"]
    )
    model.fit(_x, _y, epochs=100, batch_size=10, verbose=0)
    return model


def identify_roi(row):
    """A descriptive docstring belongs here."""
    prediction = NNET.predict(
        np.array(
            [
                [
                    float(row["Area"]),
                    float(row["Perim."]),
                    float(row["Major"]),
                    float(row["Minor"]),
                    float(row["Circ."]),
                    float(row["Feret"]),
                    float(row["MinFeret"]),
                    float(row["AR"]),
                    float(row["Round"]),
                    float(row["Solidity"]),
                ]
            ]
        ),
        verbose=0,
    )
    return prediction[0].argmax()


def analyze_results(folder):
    """A descriptive docstring belongs here."""
    args = os.path.basename(folder).split("_")
    isolate = args[0]
    treatment = args[1]
    results = [
        csv_handler(os.path.join(folder, csv_file)) for csv_file in os.listdir(folder)
    ]
    headers = ["Classification", "Count", "Percentage"]
    # [a, d, g, n]
    counts = [0, 0, 0, 0]
    for result in results:
        counts[0] += result[0]
        counts[1] += result[1]
        counts[2] += result[2]
        counts[3] += result[3]
    total = sum(counts)
    output_data = [
        ["Appressoria", counts[0], round(counts[0] / total * 100, 1)],
        ["Germinated", counts[2], round(counts[2] / total * 100, 1)],
        ["Ungerminated", counts[3], round(counts[3] / total * 100, 1)],
        ["Debris", counts[1], round(counts[1] / total * 100, 1)],
    ]
    # Write the results to the output file
    with open(
        f"results/{isolate}_{treatment}.csv",
        "w",
        encoding="utf-8",
        newline="",
    ) as csv_outfile:
        csv_writer = csv.writer(csv_outfile)
        csv_writer.writerow(headers)
        for row in output_data:
            csv_writer.writerow(row)
    # Print a table of the results for the user
    print(f"* Results for isolate {isolate.upper()} treated with {treatment.upper()}")
    print(tabulate(output_data, headers=headers))


# handle csv datasets
def csv_handler(input_file):
    """Read CSV file produced by ImageJ and analyze each ROI using logistic regression."""
    # [a, d, g, n]
    image_data = [0, 0, 0, 0]
    # open csv file
    with open(
        input_file,
        "r",
        encoding="utf-8",
    ) as csv_file:
        # read csv as a dict so header is skipped and value lookup is simpler
        csv_reader = csv.DictReader(csv_file, delimiter=",")
        for row in csv_reader:
            image_data[identify_roi(row)] += 1
    return image_data


def main(folder):
    """Execute the main objective."""
    global NNET
    os.chdir(os.path.dirname(__file__))
    NNET = setup_neural_network()
    analyze_results(folder)


if __name__ == "__main__":
    if len(sys.argv) == 2:
        main(sys.argv[1])
    else:
        sys.exit(f"Usage: {sys.argv[0]} [FOLDER]")
