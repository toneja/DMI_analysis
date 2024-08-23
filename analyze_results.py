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
from tabulate import tabulate

# globals
REGR = ""


def setup_regression(model):
    """Setup the logistic regressions used to determine ROI identity."""
    dataset = pandas.read_csv(f"models/{model}_training_data.csv")
    _x = dataset[["Perim.", "Major", "Minor", "Feret", "MinFeret", "Round", "Solidity"]]
    _y = dataset["class"]
    regression = LogisticRegression(solver="saga", max_iter=5000)
    regression.fit(_x.values, _y)
    return regression


def identify_roi(row):
    """A descriptive docstring belongs here."""
    prediction = REGR.predict(
        [
            [
                float(row["Perim."]),
                float(row["Major"]),
                float(row["Minor"]),
                float(row["Feret"]),
                float(row["MinFeret"]),
                float(row["Round"]),
                float(row["Solidity"]),
            ]
        ]
    )
    return prediction[0]


def analyze_results(folder):
    """A descriptive docstring belongs here."""
    args = os.path.basename(folder).split("_")
    isolate = args[0]
    treatment = args[1]
    results = [
        csv_handler(os.path.join(folder, csv_file)) for csv_file in os.listdir(folder)
    ]
    headers = ["Classification", "Count", "Percentage"]
    counts = [0, 0, 0, 0]
    for result in results:
        counts[0] += result["a"]
        counts[1] += result["g"]
        counts[2] += result["n"]
        counts[3] += result["d"]
    total = sum(counts)
    output_data = [
        ["Appressoria", counts[0], round(counts[0] / total * 100, 1)],
        ["Germinated", counts[1], round(counts[1] / total * 100, 1)],
        ["Ungerminated", counts[2], round(counts[2] / total * 100, 1)],
        ["Debris", counts[3], round(counts[3] / total * 100, 1)],
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
    image_data = {
        "a": 0,
        "g": 0,
        "n": 0,
        "d": 0,
    }
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
    global REGR
    os.chdir(os.path.dirname(__file__))
    REGR = setup_regression("appressoria")
    analyze_results(folder)


if __name__ == "__main__":
    if len(sys.argv) == 2:
        main(sys.argv[1])
    else:
        sys.exit(f"Usage: {sys.argv[0]} [FOLDER]")
