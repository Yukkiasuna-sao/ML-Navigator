import unittest
from datetime import datetime, timedelta

import numpy as np
import pandas as pd

from preprocessing.data_science_help_functions import (
    detect_id,
    detect_target,
    detect_problem_type,
    adversarial_validation,
)

# create dataframe for testing the preprocessing functions:
def create_dataframe(seed):
    #random_state.seed(seed)
    random_state = np.random.RandomState(seed=seed)

    integer_array = random_state.randint(2, size=(100, 2))
    for catagories_numbers in range(5, 50, 10):
        integer_array = np.append(
            integer_array, random_state.randint(catagories_numbers, size=(100, 2)), axis=1
        )
    integer_columns = [f"int_col_{x}" for x in range(integer_array.shape[1])]
    continuous_array = random_state.randn(100, 10)
    continuous_columns = [f"cont_col_{x}" for x in range(continuous_array.shape[1])]
    string_array = [
        "pizza",
        "ball",
        "star3",
        "car",
        "01515",
        "cat75",
        "moon",
        "lol",
        "dddd",
        "wtf",
        "xXx",
        "82008",
        "mailbox",
    ]
    string_arrays = random_state.choice(string_array, (100, 10))
    string_columns = [f"string_col_{x}" for x in range(string_arrays.shape[1])]
    integer_dataframe = pd.DataFrame(integer_array, columns=integer_columns)
    continuous_dataframe = pd.DataFrame(continuous_array, columns=continuous_columns)
    string_dataframe = pd.DataFrame(string_arrays, columns=string_columns)
    date_array = np.array([datetime.now() - timedelta(days=x) for x in range(100)]).reshape(
        100, 1
    )
    date_dataframe = pd.DataFrame(date_array, columns=["date_col"])
    return pd.concat(
        [date_dataframe, integer_dataframe, continuous_dataframe, string_dataframe], axis=1
        )

train_dataframe = create_dataframe(100)
test_dataframe = create_dataframe(10000)

dataframe_dict = {
    "train": train_dataframe,
    "valid": train_dataframe,
    "test": train_dataframe,
}

id_set = detect_id(dataframe_dict)
target_set = detect_target(dataframe_dict)
problem_type_dict = detect_problem_type(dataframe_dict, target_set)


class TooManyOptions(unittest.TestCase):
    def test_train_dataset(self):
        self.assertEqual(id_set, "Too many options for ids. Not possible to detect id")
        self.assertEqual(
            target_set, "Too many options for target. Not possible to detect target"
        )
        self.assertEqual(problem_type_dict, "No problem type to detect")


dataframe_dict = {
    "train": train_dataframe,
}

id_set_2 = detect_id(dataframe_dict)
print(id_set_2)
target_set_2 = detect_target(dataframe_dict)
print(target_set_2)
problem_type_dict_2 = detect_problem_type(dataframe_dict, target_set_2)
print(problem_type_dict_2)


class OneDataFrame(unittest.TestCase):
    def test_train_dataset(self):
        self.assertEqual(
            id_set_2, "Too many options for ids. Not possible to detect id"
        )
        self.assertEqual(
            target_set_2, "Too many options for target. Not possible to detect target"
        )
        self.assertEqual(problem_type_dict_2, "No problem type to detect")


two_train_dataframes_dict = {"train": train_dataframe, "test": test_dataframe}
adversarial_validation_score = adversarial_validation(two_train_dataframes_dict, ['date_col'])



class SameDataFrame(unittest.TestCase):
    def test_adversarial_validation(self):
        # test and train are completely random so result of validation should be around 0.5
        self.assertTrue(0.45 <= adversarial_validation_score <= 0.55)


if __name__ == "__main__":
    unittest.main()
