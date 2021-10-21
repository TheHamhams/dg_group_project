import logging
import yaml
import re
from os.path import getsize
import gzip
from matplotlib import pyplot as plt
import seaborn as sns

def read_config(path):
    with open(path, 'r') as stream:
        try:
            return yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            logging.error(exc)
            
def replacer(string, char):
    pattern = char + '{2,}'
    string = re.sub(pattern, char, string) 
    return string

            
def col_header_val(df, table_config):
    df.columns = df.columns.str.lower()
    df.columns = df.columns.str.replace('[^\w]','_',regex=True)
    df.columns = list(map(lambda x: x.strip('_'), list(df.columns)))
    df.columns = list(map(lambda x: replacer(x,'_'), list(df.columns)))
    expected_col = list(map(lambda x: x.lower(),  table_config['columns']))
    expected_col.sort()
    df.columns =list(map(lambda x: x.lower(), list(df.columns)))
    df = df.reindex(sorted(df.columns), axis=1)
    
    if len(df.columns) == len(expected_col) and list(expected_col) == list(df.columns):
        print('Columns names and length validattion passed!')
        return 1
    else:
        print('Column names and length validation failed')
        mismatched_columns_file = list(set(df.columns).difference(expected_col))
        print(f'The following file columns are not present in the YAML file: {mismatched_columns_file}')
        missing_YAML_file = list(set(expected_col).difference(df.columns))
        print(f'The following YAML columns are not in the uploaded file: {missing_YAML_file}')
        logging.info(f'df_columns: {df.columns}')
        logging.info(f'expected_columns: {expected_col}')
        return 0

def check_results(validation, df, name):    
    if validation == 0:
        print('Validation failed')
    else:
        print('Validation passed')
        make_file(df, name)
        
        
    
def make_file(df, name):
    text = yaml.dump(
    df.reset_index().to_dict(orient='records'),
    sort_keys=False, width=72, indent=4,
    default_flow_style=None)
    f = gzip.open(f'{name}.txt.gz', 'wb')
    f.write(text)
    f.close()

    
def df_info(df, name):
    size = getsize(name) / 1024**2
    print(f"""
    Number of columns: {len(df.columns)}
    Number of rows: {len(df)}
    File size: {round(size, 2)}MB 
    """)   

def columns_graph(df):
    for i in df.columns:
        if df[i].dtype == 'int64':
            plt.hist(df[i])
            plt.title(i)
            plt.show()
            plt.clf()
        else:
            sns.barplot(df[i].value_counts().index,df[i].value_counts()).set_title(i)
            plt.show()