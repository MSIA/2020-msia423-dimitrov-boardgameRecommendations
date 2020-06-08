"""
This module contains 12 unit tests for the 6 functions that create features from the clean json data
There is 1 happy and one unhappy path tested for each function.
"""

import pandas as pd
import pytest
import json

from src.featurize import load_unfeaturized_data, expand_feature, one_hot_encode, collapse_one_hot_encoded, merge_original_with_collapsed, extract_stats


# Happy path for load_unfeaturized_data()
def test_load_unfeaturized_data():

    data = {'key1': [1,2,3], 'key2':[4,5,6]}
    filepath = 'data/test.json'

    with open(filepath, "w") as write_file:
        json.dump(data, write_file)

    loaded_data = load_unfeaturized_data(filepath)
    assert loaded_data.keys() == data.keys()


# Unhappy path for load_unfeaturized_data()
def test_load_unfeaturized_data_file_not_found():
    # Bad Input
    filepath = ''

    with pytest.raises(SystemExit) as pytest_error:
        load_unfeaturized_data(filepath)
    assert pytest_error.type == SystemExit


# Happy path for expand_feature()
def test_expand_feature():
    data = {'name': ['Catan', 'Monopoly'],
            'categories': [['category1'], ['category2', 'category3']],
            'mechanics': [['mechanic1', 'mechanic2'], ['mechanic3']]}

    correct_result = {'name': ['Catan', 'Monopoly', 'Monopoly'],
                    'categories': ['category1', 'category2', 'category3'],
                    'mechanics': [['mechanic1', 'mechanic2'], ['mechanic3'], ['mechanics3']]}

    df = pd.DataFrame(data)

    expanded_features_data = expand_feature(df, 'categories')

    assert list(correct_result['name']) == list(expanded_features_data['name'])
    assert list(correct_result['categories']) == list(expanded_features_data['categories'])

# Unhappy path
def test_expand_feature_missing_column():
    # Bad data
    data = {'name': ['Catan', 'Monopoly'],
            'mechanics': [['mechanic1', 'mechanic2'], ['mechanic3']]}
    df = pd.DataFrame(data)

    with pytest.raises(SystemExit) as pytest_error:
        expand_feature(df, 'categories')
    assert pytest_error.type == SystemExit


# Happy path
def test_one_hot_encode():
    data = {'name': ['Catan', 'Monopoly', 'Monopoly'],
                      'categories': ['category1', 'category2', 'category3']}

    df = pd.DataFrame(data)

    correct_result = {'name': ['Catan', 'Monopoly', 'Monopoly'],
                      'categories_category1':[1,0,0],
                      'categories_category2':[0,1,0],
                      'categories_category3':[0,0,1]}

    assert list(correct_result['name']) == list(one_hot_encode(df, 'categories')['name'])
    assert list(correct_result['categories_category1']) == list(one_hot_encode(df, 'categories')['categories_category1'])
    assert list(correct_result['categories_category2']) == list(one_hot_encode(df, 'categories')['categories_category2'])
    assert list(correct_result['categories_category3']) == list(one_hot_encode(df, 'categories')['categories_category3'])

# Unhappy path
def test_one_hot_encode_missing_column():
    # Bad data
    data = {}
    df = pd.DataFrame(data)

    with pytest.raises(SystemExit) as pytest_error:
        one_hot_encode(df, 'categories')
    assert pytest_error.type == SystemExit


# Happy path
def test_collapse_one_hot_encoded():
    data = {'id': ['123', '234', '234'],
                      'categories_category1': [1, 0, 0],
                      'categories_category2': [0, 1, 0],
                      'categories_category3': [0, 0, 1]}

    correct_result = {'id': ['123', '234'],
                      'categories_category1': [1, 0],
                      'categories_category2': [0, 1],
                      'categories_category3': [0, 1]
                      }

    df = pd.DataFrame(data)

    assert list(correct_result['categories_category1']) == list(collapse_one_hot_encoded(df, 1)['categories_category1'])
    assert list(correct_result['categories_category2']) == list(collapse_one_hot_encoded(df, 1)['categories_category2'])
    assert list(correct_result['categories_category3']) == list(collapse_one_hot_encoded(df, 1)['categories_category3'])


# Unhappy path
def test_collapse_one_hot_encoded_missing_id():
    # bad data
    data = {'categories_category1': [1, 0, 0],
            'categories_category2': [0, 1, 0],
            'categories_category3': [0, 0, 1]}

    df = pd.DataFrame(data)

    for col in df.columns:
        assert list(df[col]) == list(collapse_one_hot_encoded(df, 1)[col])


# Happy path
def test_merge_original_with_collapsed():
    df_1 = pd.DataFrame({'id': ['123', '234'],
                      'categories_category1': [1, 0],
                      'categories_category2': [0, 1],
                      'categories_category3': [0, 1]
                      })

    df_2 = pd.DataFrame({'id':['123', '234'],
                         'column':['value1', 'value2']
                         })

    correct_result = pd.DataFrame({'id': ['123', '234'],
                                   'column': ['value1', 'value2'],
                                   'categories_category1': [1, 0],
                                   'categories_category2': [0, 1],
                                   'categories_category3': [0, 1]
                      })

    for col in correct_result.columns:
        assert list(correct_result[col]) == list(merge_original_with_collapsed(df_1, df_2)[col])


# Unhappy path
def test_merge_original_with_collapsed_missing_key():
    # Bad data - missing 'id' (key to join on)
    df_1 = pd.DataFrame({'categories_category1': [1, 0],
                         'categories_category2': [0, 1],
                         'categories_category3': [0, 1]
                         })

    df_2 = pd.DataFrame({'id': ['123', '234'],
                         'column': ['value1', 'value2']
                         })

    with pytest.raises(SystemExit) as pytest_error:
        merge_original_with_collapsed(df_1, df_2)
    assert pytest_error.type == SystemExit


# Happy path for extract_stats()
def test_extract_stats_schema():
    data = [{'id': 174430,
            'name': 'Gloomhaven',
            'stats': {'usersrated': 34855,
                      'average': 8.8311,
                      'bayesaverage': 8.57594,
                      'stddev': 1.60889,
                      'median': 0.0,
                      'owned': 56031,
                      'trading': 347,
                      'wanting': 1417,
                      'wishing': 14655,
                      'numcomments': 6553,
                      'numweights': 1497,
                      'averageweight': 3.827
               }
            },
            {'id': 123456,
             'name': 'Some Other Game',
             'stats': {'usersrated': 34855,
                       'average': 8.8311,
                       'bayesaverage': 8.57594,
                       'stddev': 1.60889,
                       'median': 0.0,
                       'owned': 56031,
                       'trading': 347,
                       'wanting': 1417,
                       'wishing': 14655,
                       'numcomments': 6553,
                       'numweights': 1497,
                       'averageweight': 3.827
                       }
             }
            ]

    df = pd.DataFrame(data)

    assert list(extract_stats(df).columns) == ['id', 'name', 'number_of_user_ratings','average_user_rating', 'number_of_user_weight_ratings',
                                               'average_user_weight_rating', 'bayes_average', 'number_of_users_own' ]


# Unhappy path
def test_extract_stats_missing_stats_column():
    # bad data
    data = {'col1': [1,2,3],
            'col2': [2,3,4]}
    df = pd.DataFrame(data)
    correct_result = df

    # Should return the same df, checking that all columns match
    for col in correct_result.columns:
        assert list(correct_result[col]) == list(extract_stats(df)[col])