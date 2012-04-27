import os
import sys
import discover

os.chdir(os.path.abspath(os.path.dirname(__file__)) + os.path.altsep + '..')

sys.path += ['../']
os.system(['clear', 'cls'][os.name == 'nt'])
discover.main()
