import pandas as pd
from typing import Tuple


def unpack_data_json(df_column : pd.DataFrame) -> pd.DataFrame:
    """Takes pandas DataFrame column as an input. Iterates rows and upacks them. Returns new dataframe as a result"""
    result = pd.DataFrame([])

    for index in range(df_column.shape[0]):
        #concats result DataFrame with json data in current row
        result = pd.concat([result, pd.json_normalize(df_column[index])])

    return result


def unpack_and_assign_id(df_column : pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Takes pandas DataFrame column as an input. Iterates rows and upacks them. Returns new dataframe and list of lists of indexes as a result"""
    #TODO: f() -> dataframe, dataframe
    
    result = pd.DataFrame([])
    indexes = list()

    for index in range(df_column.shape[0]):
        #extract and append list of indexes
        ingr = pd.json_normalize(df_column[index])
        indexes.append(ingr['id'].to_list())

        #concats result DataFrame with json data in current row
        result = pd.concat([result, ingr])

    # idx = pd.DataFrame({df_column.name + 'ID' : indexes})
    return result, indexes


def analyze_ingredients(data : pd.DataFrame, ingredients : pd.DataFrame) -> pd.DataFrame:
    """Takes DataFrame as an input and outputs list of all ingredients (records from separate DataFrame) found in the 'ingredientsID' tab."""
    #set new indexing in list
    data = data.reset_index()
    #initialize new DataFrame
    cocktail_ingr = pd.DataFrame([])

    for index in range(data.shape[0]):
        ingr_list = data['ingredientsID'][index]
        mask = ingredients['id'].isin(ingr_list)
        
        #update new DataFrame
        to_append = ingredients.loc[mask]
        cocktail_ingr = pd.concat([cocktail_ingr, to_append])

    return cocktail_ingr