"""
This module contains 8 unit tests for functions that extract features and train a KMeans model in model.py
"""

import pandas as pd
import numpy as np
import pytest
import json
import sklearn.cluster
from sklearn.cluster import KMeans

from src.model import load_featurized_data, extract_features, standardize_features, fit_kmeans, model_predict, evaluate_silhouette


# Happy path for load_featurized_data()
def test_load_featurized_data():

    data = {'key1': [1,2,3], 'key2':[4,5,6]}
    filepath = 'data/test.json'

    with open(filepath, "w") as write_file:
        json.dump(data, write_file)

    df = pd.DataFrame(data)
    loaded_data = load_featurized_data(filepath)
    # Check that all columns are loaded as expected
    for ii in range(len(loaded_data.columns)):
        assert loaded_data.columns[ii] == df.columns[ii]


# Unhappy path for load_featurized_data()
def test_load_featurized_data_file_not_found():
    # Bad Input
    filepath = ''

    with pytest.raises(SystemExit) as pytest_error:
        load_featurized_data(filepath)
    assert pytest_error.type == SystemExit


# Happy path
def test_extract_features():
    data = {'id':[1], 'name':[1], 'image':[1], 'thumbnail':[1], 'artists':[1], 'publishers':[1],
                           'designers':[1], 'description':[1], 'categories':[1], 'mechanics':[1], 'column':[1]}

    df = pd.DataFrame(data)

    assert extract_features(df).columns == ['column']


# Unhappy path
def test_extract_features_missing_columns():
    # bad data missing id column, whcih is supposed to be removed
    data = {'name': [1], 'image': [1], 'thumbnail': [1], 'artists': [1], 'publishers': [1],
            'designers': [1], 'description': [1], 'categories': [1], 'mechanics': [1], 'column': [1]}

    df = pd.DataFrame(data)
    # Supposed to return same df with the same columns
    for col in df.columns:
        assert list(df[col]) == list(extract_features(df)[col])


# Happy path
def test_standardize_features():
    data = {'col1': [1,2,3], 'col2': [2,3,4]}
    df = pd.DataFrame(data)
    print((standardize_features(df)))
    assert isinstance(standardize_features(df), np.ndarray)


# Unhappy path
def test_standardize_features_empty_df():

    # Bad data
    data = {'col1':[1], 'col2':[2]}
    df = pd.DataFrame(data)


    for col in df.columns:
        assert list(df[col]) == list(extract_features(df)[col])


# Happy path
def test_fit_kmeans_type():
    X = [[1, 2], [2, 3], [3, 4]]

    assert isinstance(KMeans(n_clusters=2).fit(X), sklearn.cluster._kmeans.KMeans)

# Unhappy path
def test_fit_kmeans_bad_seed():
    bad_seed = 1.5
    X = [0,1,3]
    k = 3

    with pytest.raises(SystemExit) as pytest_error:
        fit_kmeans(X, k, bad_seed)
    assert pytest_error.type == SystemExit

# NOTE
# Don't need tests for model_predict() & evaluate_silhouette(),
# because they are essentially just wrappers for sklean functions
