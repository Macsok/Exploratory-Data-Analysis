import pandas as pd
from typing import Tuple
from IPython.display import display
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.cluster import KMeans


def unpack_data_json(df_column: pd.DataFrame) -> pd.DataFrame:
    """Takes pandas DataFrame column as an input. 
    Iterates rows and upacks them. Returns new dataframe as a result"""
    result = pd.DataFrame([])

    for index in range(df_column.shape[0]):
        #concats result DataFrame with json data in current row
        result = pd.concat([result, pd.json_normalize(df_column[index])])

    return result


def unpack_and_assign_id(
        df_column: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Takes pandas DataFrame column as an input. 
    Iterates rows and upacks them. 
    Returns new dataframe and list of lists of indexes as a result"""
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


def analyze_ingredients(
        data: pd.DataFrame,
        ingredients: pd.DataFrame) -> pd.DataFrame:
    """Takes DataFrame as an input and outputs list of all ingredients 
    (records from separate DataFrame) found in the 'ingredientsID' tab."""
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


def dataset_preprocessing(
        df: pd.DataFrame, 
        drop_times: bool = True) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Preprocesses provided dataset (specified for cocktail_dataset). 
    Returns tuple of pd.DataFrame, [df, ingredniets_column]. 
    Set drop_times to False to get timestamps"""

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


def ingredients_to_names(ingredients: pd.DataFrame, 
                         ingredients_list: pd.DataFrame) -> pd.DataFrame:
    """Matches each ingredients list with names, returns a column of names in lists. 
    Set to_list option to True to get results in list."""
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


def recommend_cocktails(cocktail_name: str, 
                        df: pd.DataFrame):
    """Takes actual cocktail name and DataFrame (with ingredients list column), 
    counts similarity between cocktails and returns 3 most matching cocktails (from most to least similar)."""

    # vectorizing ingredients
    vectorizer = CountVectorizer()
    ingredient_matrix = vectorizer.fit_transform(df['ingredients'])

    # cosine similarity matrix
    similarity_matrix = cosine_similarity(ingredient_matrix)

    indices = pd.Series(df.index, index=df['name']).drop_duplicates()
    idx = indices[cocktail_name]
    
    # sorting according to similarity
    sim_scores = list(enumerate(similarity_matrix[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    
    # choose 3 most matching ones
    sim_scores = sim_scores[1:4]
    cocktail_indices = [i[0] for i in sim_scores]
    
    return df['name'].iloc[cocktail_indices].to_list()


def print_similar_cocktails(df: pd.DataFrame, 
                            similar_to: str) -> None:
    """Prints most similar cocktails to provided one."""
    print('Your cocktail:')
    display(df.loc[ df['name'] == similar_to])
    print('Suggested coctails (most similar at the top):')
    res = pd.DataFrame([])
    for one in recommend_cocktails(similar_to, df): res = res.append(df.loc[ df['name'] == one], ignore_index=True)
    display(res)


def clusterization(df: pd.DataFrame, 
                   clusters: int) -> pd.DataFrame:
    """Clusters provided DataFrame by similarity of ingredients used."""
    # vectoriznig and clustering using scikit-learn
    vectorizer = CountVectorizer()
    ingredient_matrix = vectorizer.fit_transform(df['ingredients'])
    kmeans = KMeans(n_clusters=clusters)
    
    return pd.DataFrame(kmeans.fit_predict(ingredient_matrix))