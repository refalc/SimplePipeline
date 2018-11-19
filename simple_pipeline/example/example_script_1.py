import datetime
import sys
import time
import os


if __name__ == '__main__':
    start_time = datetime.datetime.now()
    time.sleep(1)
    end_time = datetime.datetime.now()

    print('example_script_1 start in {} end in {} with arg_list {} in dir {}'.format(start_time, end_time, sys.argv,
                                                                                     os.getcwd()))
