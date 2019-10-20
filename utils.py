import os.path as path
import pandas as pd


def assert_msg(condition, message):
    if not condition:
        raise Eception(message)
        

def read_file(filename):
    # Get the absolute path of file
    file_path = path.join(path.dirname(__file__), filename)
    
    # Check whether the file exists or not
    assert_msg(path.exists(file_path), 'File does not exist!')
    
    # Read CSV file and return
    return pd.read_csv(file_path,
                       index_col = 0,
                       parse_dates = True,
                       infer_datetime_format = True)


def SMA(values, k):
    """
    Return the Simple Moving Average
    """
    return pd.Series(values).rolling(k).mean()


def crossover(series1, series2) -> bool:
    """
    Check whether two series cross at the end
    :param series1:  series1
    :param series2:  series2
    :return:         True when cross, False otherwise
    """    
    return series1[-2] < series2[-2] and series1[-1] > series2[-1]