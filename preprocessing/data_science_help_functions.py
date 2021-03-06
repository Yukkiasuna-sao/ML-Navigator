import logging
import operator
import os
from collections import Counter
from typing import Tuple, List, Dict, Set, Union

import pandas as pd
import xgboost as xgb
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold

logger = logging.getLogger(__name__)
formatting = (
    "%(asctime)s: %(levelname)s: File:%(filename)s Function:%(funcName)s Line:%(lineno)d "
    "message:%(message)s"
)
logging.basicConfig(
    filename=os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs/logs.log"),
    level=logging.INFO,
    format=formatting,
)


def detect_id(dataframes_dictionary: dict) -> Union[set, str]:
    """ ID candidates detector

    the following assumptions are considered:

    | 1. Id exists in all the loaded datasets;
    | 2. All the id' values are unique in all datasets;
    | 3. There are no missing values.

    If the function finds more than one feature that satisfies the assumptions, it suggests a list of candidates
    and the user has to decide which one is the id

    :param dict dataframes_dictionary: It is a dictionary that contains pandas dataframes e.g. dataframes_dictionary ={
    'train': train_dataframe, 'test': test_dataframe}

    :return A set of strings values as id candidates.

    :rtype: set
    """

    id_candidates = []

    for key_i, dataframe in dataframes_dictionary.items():
        for column_i in dataframe.columns:
            if len(dataframe[column_i].value_counts()) == dataframe[column_i].count() and \
                    len(dataframe[column_i].value_counts()) == dataframe.shape[0]:
                logger.info(f"{column_i} found to be a candidate as an ID")

                id_candidates.append(column_i)

    id_candidates = set(id_candidates)

    # the number 5 in the if statement should be defined as variable later that can be added by the user
    if len(id_candidates) > 5:
        logger.info("Too many options for ids.")
        return "Too many options for ids. Not possible to detect id"
    elif len(id_candidates) == 0:
        logger.info("No ids candidates were found")
        return "No ids candidates were found"

    logger.info("Detecting the id is finished")

    return set(id_candidates)


def detect_target(dataframes_dictionary: dict) -> Union[list, str]:
    """ Target candidates detector

    The following assumptions are considered:

    | 1. Target is missing in at least one dataset-which is the test dataset usually;
    | 2. The target has no missing values.

    If the function finds more than one feature that satisfies the assumptions, it suggests a list of candidates
    and the user has to decide which one is the target

    :param dict dataframes_dictionary: It is a dictionary that contains pandas dataframes e.g. dataframes_dictionary ={
    'train': train_dataframe, 'test': test_dataframe}

    :return
        target_candidates_2: A list of candidates as strings that satisfies the two mentioned assumptions above

    :rtype: list

    """

    target_candidates_1 = []
    target_candidates_2 = []
    columns = []

    for key_i, dataframe in dataframes_dictionary.items():
        # Getting all columns names of all datasets in one place
        columns = columns + list(dataframe.columns)

    # check the first assumptions: calculating the occurrence
    try:
        occurrence = Counter(columns)
        minimum_occurrence = min(occurrence.values())
        target_candidates_1 = [x for x, y in occurrence.items() if y == minimum_occurrence]
        logger.info("Checking the first assumption (occurrence) for finding the target is done!")

    except Exception as e:
        logger.error(f"Error: {e}")

    # check the second assumption: No missing values
    for column_i in target_candidates_1:
        for key_i, dataframe in dataframes_dictionary.items():
            if column_i in dataframe.columns:
                if len(dataframe[column_i]) - dataframe[column_i].count() == 0:
                    target_candidates_2.append(column_i)

    logger.info("Checking the second assumption (missing values) for finding the target is done!")

    if len(target_candidates_2) == 0:
        logger.info("No target was detected")
        return "No target was detected"
    elif len(target_candidates_2) > 5:
        logger.info("Too many options for target")
        return "Too many options for target. Not possible to detect target"

    logger.info("Detecting the target is finished")

    return target_candidates_2


def detect_problem_type(dataframes_dictionary: dict,
                        target_candidates: list,
                        threshold: float = 0.1) -> Union[dict, str]:
    """ Problem type detector

    This function tells what type of problem that should be solved: classification or regression

    :param dict dataframes_dictionary: A dictionary that contains pandas dataframes e.g. dataframes_dictionary ={
                                        'train': train_dataframe, 'test': test_dataframe}
    :param list target_candidates: It is list of string of the possible target candidates
    :param float threshold: A value larger than 0 and less than 1. It defines when the problem is considered as a
    regression  problem or classification problem

    :return:
            problem_type: dictionary of target candidates associated with the problem type

    :rtype: dict
    """

    problem_type = {}

    if isinstance(target_candidates, list) and len(target_candidates) > 0:
        for column_i in target_candidates:
            for key_i, dataframe in dataframes_dictionary.items():
                if column_i in dataframe.columns:
                    if len(dataframe[column_i].value_counts()) / dataframe.shape[0] < threshold:
                        problem_type[column_i] = "classification"
                        logger.debug(f"For the target {column_i}: classification")
                    else:
                        problem_type[column_i] = "regression"
                        logger.debug(f"For the target {column_i}: regression")

    else:
        logger.info("No valid target candidates")
        return "No problem type to detect"

    logger.info("Detecting the problem type is finished")

    return problem_type


def detect_id_target_problem(dataframes_dict: dict, threshold: float = 0.1) -> Tuple[Set, List, Dict]:
    """ ID Target Problem type detector

    This function tries to find which column is the ID and which one is the target and what type of the problem
    to be solved. It uses `detect_id`, `detect_target` and `detect_problem_type` functions.

    :param dict dataframes_dict: A dictionary that contains pandas dataframes e.g. dataframes_dictionary ={
                'train': train_dataframe, 'test': test_dataframe}
    :param float threshold: A value larger than 0 and less than 1. It defines when the problem is a regression
            problem or classification problem

    :return:
            | possible_ids: A list of candidates as strings.
            | possible_target: list of candidates as strings.
            | possible_problems: dictionary of target candidates associated with the problem type.
    """

    possible_ids = detect_id(dataframes_dict)
    possible_target = detect_target(dataframes_dict)
    possible_problems = detect_problem_type(dataframes_dict, possible_target, threshold=threshold)

    logger.info("Running all the process to detect id, target and the problem type is finished")

    # Showing the info to the user
    print(f"The possible ids are:\n {possible_ids}")
    print(f"The possible possible_target are:\n {possible_target}")
    print(f"The type of the problem that should be solved:\n {possible_problems}")
    return possible_ids, possible_target, possible_problems


# result printing
def form_template(result, train_label, test_label, adversarial_validation_result, threshold) -> str:
    """ Validation template former

    This function put together all results of adversarial validation

    :param Result related values: train_label, test_label, adversarial_validation_result, threshold

    :return:
           - A formed string
    """

    return f"{result} significant difference between {train_label} and {test_label} datasets\n" \
           f"in terms of feature distribution. Validation score: {adversarial_validation_result}, threshold: {threshold}"


def adversarial_validation(dataframe_dict: dict,
                           ignore_columns: list,
                           max_dataframe_length: int = 100000,
                           threshold: float = 0.7) -> Union[float, None]:
    """ Make adversarial validation checking

    Training a probabilistic classifier to distinguish train/test examples.
    See more info here: http://fastml.com/adversarial-validation-part-one/
    This function checks whether test and train data coming from the same data distribution.

    :param dataframe_dict:
D, target, etc...)
    :param float threshold: A value larger than 0 and less than 1. If the conclusion of calculation is greater than threshold - there is sugnificant difference between train and test data

    :return:
            - adversarial_validation_result: Adversarial validation score.
    """
    print('Applying adversarial validation technique to check whether test and train data are coming from the same data distribution...')
    # Check if it only one dataframe provided
    if len(dataframe_dict) != 2:
        # do nothing and return the original data
        print("Can't apply adversarial_validation because count of dataframes is not equal to 2")
        return

    # TODO: support > 2 dataframes ISSUE#44
    # if 2 dataframe than it will be considered as `train` and `test`

    # TODO: replace to take_first_n ISSUE 45 from https://docs.python.org/3.8/library/itertools.html#itertools-recipe
    label_iter = iter(dataframe_dict.keys())
    train_label = next(label_iter)
    test_label = next(label_iter)

    train = dataframe_dict[train_label]
    test = dataframe_dict[test_label]

    df_joined = join_dataframe_for_validation(ignore_columns, max_dataframe_length, test, train)

    # a new target
    y = df_joined['istrain']
    df_joined.drop('istrain', axis=1, inplace=True)

    # train classifier
    adversarial_validation_result, clf = get_adv_validation_score(df_joined, y)

    # Process conclusion:
    if adversarial_validation_result < threshold:
        conclusion = 'There is no'
        print(form_template(conclusion, train_label, test_label, adversarial_validation_result, threshold))
    else:
        conclusion = 'WARNING!!!! There is'
        print(form_template(conclusion, train_label, test_label, adversarial_validation_result, threshold))
        print(f"Top features are: {xgb_important_features(clf)}\n")
    return adversarial_validation_result


def join_dataframe_for_validation(ignore_columns: list,
                                  max_dataframe_length: int,
                                  test: pd.DataFrame,
                                  train: pd.DataFrame) -> pd.DataFrame:
    """Join dataframe for validation

    :param test:
    :param train:
    :param list ignore_columns: List of column to ignore (ID, target, etc...)
    :param int max_dataframe_length: a limit of dataframe length before joining
    :return:
            - df_joined: Joined dataframe.
    """

    if len(ignore_columns) > 0:
        columns_to_use = [x for x in list(test.columns) if x not in ignore_columns]
        train = train[columns_to_use]
        test = test[columns_to_use]

    # max_dataframe_length
    for df in [train, test]:
        if len(df) > max_dataframe_length:
            df = df.head(max_dataframe_length)

    # add identifier and combine
    train['istrain'] = 1
    test['istrain'] = 0
    df_joined = pd.concat([train, test], axis=0)
    # convert non-numerical columns to integers
    df_numeric = df_joined.select_dtypes(exclude=['object', 'datetime'])
    df_obj = df_joined.select_dtypes(include=['object', 'datetime']).copy()
    for c in df_obj:
        df_obj[c] = pd.factorize(df_obj[c])[0]
    df_joined = pd.concat([df_numeric, df_obj], axis=1)
    return df_joined


def get_adv_validation_score(df_joined: pd.DataFrame,
                             y: pd.Series) -> Tuple[float, xgb.sklearn.XGBClassifier]:
    """ Advisarial validation score estimator

    Calculate advisarial validation score based on dataframes and XGBClassifier

    :param DataFrame df_joined: Feature dataframe
    :param Series y: Target series

    :return:
            - clf: Trained model
            - mean of KFold validation results (ROC-AUC scores)
    """

    skf = StratifiedKFold(n_splits=3, shuffle=True, random_state=44)
    xgb_params = {}
    clf = xgb.XGBClassifier(**xgb_params, seed=10)
    results = []
    logger.info('Adversarial validation checking:')
    for fold, (train_index, test_index) in enumerate(skf.split(df_joined, y)):
        fold_xtrain, fold_xval = df_joined.iloc[train_index], df_joined.iloc[test_index]
        fold_ytrain, fold_yval = y.iloc[train_index], y.iloc[test_index]
        clf.fit(fold_xtrain, fold_ytrain, eval_set=[(fold_xval, fold_yval)],
                eval_metric='logloss', verbose=False, early_stopping_rounds=10)
        fold_ypred = clf.predict_proba(fold_xval)[:, 1]
        fold_score = roc_auc_score(fold_yval, fold_ypred)
        results.append(fold_score)
        logger.info(f"Fold: {fold + 1} shape: {fold_xtrain.shape} score: {fold_score}")

    return round(sum(results)/len(results), 2), clf


def xgb_important_features(model: xgb.sklearn.XGBClassifier,
                           top_features: int = 5) -> str:
    """ Important features extractor

    Get top of the most important features from a trained model

    :param XGBClassifier model: A trained model
    :param int top_features: Max length of features to send back

    :return:
            - A string with a list of the most important features plus their importance
    """

    # get features
    feat_imp = model.get_booster().get_score(importance_type='gain')

    sorted_x = round_and_sort_dict(feat_imp)

    return str(sorted_x[:top_features])


def round_and_sort_dict(feat_imp: dict) -> list:
    """ Round and sort a dictionary

    :param dict feat_imp: A dictionary

    :return:
            - A sorted list
    """

    # round importances
    for dict_key in feat_imp:
        feat_imp[dict_key] = round(feat_imp[dict_key])

    # sort by importances
    sorted_x = sorted(feat_imp.items(), key=operator.itemgetter(1))
    sorted_x.reverse()

    return sorted_x
