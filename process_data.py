## Data Processing
# from data frame to readable data

import pandas as pd
from typing import Set

def get_average_nutrition_each_column(df):
    """
    Generates a dictionary for each column of the dataframe with its average
    Outputs a default dictionary where missing keys have values "Not Provided"
    """
    nutrients = df.columns
    averages = {}  # default value for missing keys

    for n in nutrients:
        averages[n] = round(df[n].mean(), 3)
    return averages


def get_union_of_keys(df1, df2):
    """
    Retrieves the union of all column names (keys) from two pandas DataFrames.
    Returns a list containing all unique column names present in either DataFrame.
    """
    # 1. Get the columns from the first DataFrame as a list
    keys_df1 = df1.columns.tolist()

    # 2. Get the columns from the second DataFrame as a list
    keys_df2 = df2.columns.tolist()

    # 3. Combine the two lists and convert to a set to get the unique union
    all_keys = set(keys_df1 + keys_df2)

    return list(all_keys)


