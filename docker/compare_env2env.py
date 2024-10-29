import argparse
from pathlib import Path

def main(env1, env2):
    '''
    Compare env files.

    Show three categories of parameters:
    Those found in both files.
    Those found only in env1.
    Those found only in env2.
    '''
  
    def to_dict(lst):
        dct = {}
        for item in lst:
            item = item.rstrip('\n')
            if not item:
                continue
            else:
                splt = item.split('=')
                assert len(splt) == 2, 'Expected 2 values after splitting at "=".'
                dct[splt[0]] = splt[1]
        
        return dct
    path1 = Path(env1)     
    path2 = Path(env2)     

    with open(path1, 'r') as f:
        data1 = f.readlines()

    with open(path2, 'r') as f:
        data2 = f.readlines()
    
    dct1 = to_dict(data1)
    dct2 = to_dict(data2)

    in_both = set(dct1.keys()).intersection(set(dct2.keys()))
    only_env1 = set(dct1.keys()).difference(set(dct2.keys()))
    only_env2 = set(dct2.keys()).difference(set(dct1.keys()))

    if in_both:
        print('=' * 79)
        print('Parameters found in both files:')
        print('-' * 79)
        for item in in_both:
            print(item)
            print(path1.name.ljust(25) + dct1[item])
            print(path2.name.ljust(25) + dct2[item])
            print('\n')
    else:
        print('No parameters found in both files.')

    if only_env1:
        print('=' * 79)
        print(f"Parameters found only in {path1.name}:")
        print('-' * 79)
        for item in only_env1:
            print(item)
            print(path1.name.ljust(25) + dct1[item])
            print('\n')

    if only_env2:
        print('=' * 79)
        print(f"Parameters found only in {path2.name}:")
        print('-' * 79)
        for item in only_env2:
            print(item)
            print(path2.name.ljust(25) + dct2[item])
            print('\n')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('env1',
        help='Path to first env file.'
    )
    parser.add_argument('env2',
        help='Path to second env file.'
    )

    args = parser.parse_args()

    main(
        args.env1,
        args.env2
    )

