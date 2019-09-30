from blessings import Terminal

# For colorful and beautiful formatted print()
term = Terminal()


class FlowInstructions():

    @staticmethod
    def read_data():
        print(term.bold(term.magenta("Please use the following function to read the data")))
        print(term.green_on_black("dataframe_dict = flow.load_data(path : str, files_list : list)"))
        print(term.bold(term.magenta("For example: ") + term.green_on_black("path = './data'")))
        print(term.bold(term.magenta(
            "If your data is in a nested directory, it is better to os.path.join. For example: ") + term.green_on_black(
            "path = os.path.join('data', 'flow_0')")))
        print(term.bold(term.magenta("For example: ") + term.green_on_black("files_list = ['train.csv','test.csv']")))
        print(term.bold(term.magenta("The output is a dictionary that contains dataframes e.g.  ")))
        print(term.blue("dataframe_dict = {'train': train_dataframe,'test': test_dataframe}"))

    @staticmethod
    def encode_categorical_features():
        print(term.bold(term.magenta("If you have categorical features with string labels, Encode the categorical "
                                     "features by applying the following function:\n") + term.green_on_black(
            "dataframe_dict, columns_set = flow.encode_categorical_feature(dataframe_dict: dict)")))

    @staticmethod
    def scale_numeric_features():
        print(term.bold(term.magenta("If you have numeric features, it is a good idea to normalize numeric features." +
                                     "Use the following function for feature normalization:\n") +
                        term.green_on_black(
                            " dataframe_dict, columns_set = flow.scale_data (dataframe_dict:"
                            " dict, ignore_columns: list)")))
        print(term.bold(term.magenta("For example: ") + term.green_on_black("ignore_columns = ['id', 'target']")))

    @staticmethod
    def train_a_model():
        print(term.bold(term.magenta("Your features are ready to train the model: ")))
        print(term.bold(term.magenta("If you want to explore the data you can run one of the following functions: ")))
        print(term.bold(term.magenta("1 . ") + term.green_on_black(
            "flow.exploring_data(dataframe_dict: dict, key_i: str)")))
        print(term.bold(term.magenta("For example: ") + term.green_on_black(
            "flow.exploring_data(dataframe_dict, 'train')")))
        print(term.bold(term.magenta("2 . ") + term.green_on_black(
            "flow.comparing_statistics(dataframe_dict: dict)")))
        print(term.bold(term.magenta("For example: ") + term.green_on_black(
            "flow.comparing_statistics(dataframe_dict)")))
        print("\n\n\n")
        print(term.bold(term.magenta("You can start training the model by applying the following function: ")))
        print(term.green_on_black("model_index_list, save_models_dir, y_test = flow.training(parameters)"))
        print('parameters = {\n'
              '     "data": {\n'
              '         "train": {"features": train_dataframe, "target": train_target}, \n'
              '         "valid": {"features": valid_dataframe, "target": valid_target}, \n'
              '         "test": {"features": test_dataframe, "target": test_target}, \n'
              '     }, \n'
              '     "split": {\n'
              '         "method": "split",\n'
              '         "split_ratios": 0.2\n'
              '         }, \n '
              '     "model": {"type": "Ridge linear regression",'
              '               "hyperparameters": {"alpha": 1,  # alpha:optimize}\n'
              '             }, \n '
              '     "metrics": ["r2_score", "mean_squared_error"]\n'
              '}')
