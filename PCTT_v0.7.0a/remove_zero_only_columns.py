import dask.dataframe as dd
from dask.diagnostics import ProgressBar
import pandas as pd
import os

def remove_zero_only_columns(input_file_path, output_file_path, chunksize=8000000000):
    temp_dir = 'temp_csv_chunks'
    os.makedirs(temp_dir, exist_ok=True)
    
    reader = pd.read_csv(input_file_path, chunksize=chunksize)

    chunk_files = []

    for i, df_chunk in enumerate(reader):
        non_zero_columns = df_chunk.loc[:, (df_chunk != 0).any(axis=0)]
        
        chunk_file = os.path.join(temp_dir, f'chunk_{i}.csv')
        non_zero_columns.to_csv(chunk_file, index=False)
        chunk_files.append(chunk_file)
    
    with ProgressBar():
        df_combined = dd.read_csv(chunk_files).compute()
        df_combined.to_csv(output_file_path, index=False)
    
    for file in chunk_files:
        os.remove(file)
    os.rmdir(temp_dir)
        
input_file_path = 'D:\\ЗАДАЧИ\\trash\\LVbnhhbq\\dэфф\\fab25f1f_tout_1_devc.csv'
output_file_path = 'D:\\ЗАДАЧИ\\trash\\LVbnhhbq\\dэфф\\fab25f1f_tout_dэфф_devc_output.csv'

remove_zero_only_columns(input_file_path, output_file_path)