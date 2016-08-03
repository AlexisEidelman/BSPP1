import os
from config import config

path_data = config['PATH']['DATA']
os.chdir(path_data)

if not os.path.exists('empty_files'):
    os.makedirs('empty_files')

for file_ in os.listdir():
    if os.stat(file_).st_size == 0:
        os.rename(file_, "empty_files/" + file_)
