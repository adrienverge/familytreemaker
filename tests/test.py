import os
#import sys
from pathlib import Path

generated_file = 'generated.txt'
input_dir = 'input'
# input test files are called i_n.txt
    # where n is number of test
input_files = sorted([i for i in Path.cwd().glob(f'{input_dir}{os.sep}i_*.txt')])
for input_file in input_files:
    input_file = input_file.name    # get just filename and convert to str
    print(f'TestCase: {input_file}')

    # expected output files are called o_n.txt
    expected_file = f'expected_output{os.sep}o' + input_file[1:]

    # generate output file
    os.system(f'python ..{os.sep}familytreemaker.py \
                {input_dir}{os.sep}{input_file} > {generated_file}')

    # check for differences between generated and expected output
    rv = os.system(f'diff {generated_file} {expected_file} >/dev/null')
    if rv == 0:
        print('    OK\n')
    else:
        print(f'    PROBLEM with TestCase: {input_file} !!!')
        os.system(f'sdiff {generated_file} {expected_file}')
        print()     # just for new line
