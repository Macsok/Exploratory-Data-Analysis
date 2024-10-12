import pandas as pd


def unpack_data_json(df_column : pd.DataFrame) -> pd.DataFrame:
    """Takes pandas dataframe column as an input. Iterates rows and upacks them. Returns new dataframe as a result"""
    result = pd.DataFrame([])

    for index in range(df_column.shape[0]):
        result = pd.concat([result, pd.json_normalize(df_column[index])])

    return result
