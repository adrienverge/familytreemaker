import os
#import sys
from pathlib import Path

generated_file = 'generated.txt'
# input test files are called i_n.txt
    # where n is number of test
for input_file in Path.cwd().glob("i_*.txt"):
    input_file = input_file.name    # get just filename and convert to str
    print(f'TestCase: {input_file}')

    # expected output files are called o_n.txt
    expected_file = 'o' + input_file[1:]

    os.system(f'python ../familytreemaker.py {input_file} > {generated_file}')

    rv = os.system(f'diff {generated_file} {expected_file}')
    if rv == 0:
        print('    OK\n')
