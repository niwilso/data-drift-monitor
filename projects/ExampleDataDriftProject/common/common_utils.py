import os
import numpy as np
from environs import Env


def format_arg_features(features):
    """ Formats the provided list of features

    Inputs:
        features (str): Single feature or list of features (e.g., 'feature1,feature2' or '["feature1","feature2"]').

    Return:
        list_of_features (list of str): Returns as Python friendly list of strings.
    """

    features = features.replace(" ", "")
    features = features.replace("[", "")
    features = features.replace("]", "")

    # Remove quotation and double quotation marks
    features = features.replace("'", "")
    features = features.replace('"', "")

    # Split by comma
    list_of_features = features.rsplit(",")

    return list_of_features
