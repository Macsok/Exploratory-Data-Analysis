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


def dataset_preprocessing(df : pd.DataFrame, drop_times = True) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Preprocesses provided dataset (specified for cocktail_dataset). Returns tuple of pd.DataFrame, [df, ingredniets_column]. Set drop_times to False to get timestamps"""

    # extracting ingredients column
    ingredients, df['ingredientsID'] = unpack_and_assign_id(df['ingredients'])

    # droping columns
    df = df.drop(columns = ['imageUrl', 'ingredients', 'tags', 'alcoholic'])
    ingredients = ingredients.drop(columns = ['imageUrl', 'measure'])

    if drop_times:
        df = df.drop(columns = ['createdAt', 'updatedAt'])
        ingredients = ingredients.drop(columns = ['createdAt', 'updatedAt'])
        return df, ingredients

    # correcting data types
    for header in ['percentage']:
        ingredients[header] = ingredients[header].apply(lambda a: 0 if pd.isna(a) else a)

    df['createdAt'] = pd.to_datetime(df['createdAt'])
    df['updatedAt'] = pd.to_datetime(df['updatedAt'])

    ingredients['createdAt'] = pd.to_datetime(ingredients['createdAt'])
    ingredients['updatedAt'] = pd.to_datetime(ingredients['updatedAt'])

    return df, ingredients


def ingredients_to_names(ingredients : pd.DataFrame, ingredients_list : pd.DataFrame, to_list = False) -> pd.DataFrame:
    """Matches each ingredients list with names, returns a column of names in lists. Set to_list option to True to get results in list."""
    # TODO: optimalization
    # intitailization, and copying the data column
    column_copy = ingredients_list.copy()

    for index in range(ingredients_list.shape[0]):
        name_list = list()
        end = len(ingredients_list[index])

        for i in range(end):
            # find and append names to list
            current = ingredients.loc[ingredients['id'] == ingredients_list[index][i]].drop_duplicates()
            current = current['name'].to_list()[0]
            name_list.append(current)

        column_copy[index] = ', '.join(name_list)
    
    return column_copy