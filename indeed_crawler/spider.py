import sys
sys.path.insert(0, '/home/taiyi/job_finder/modules/')
from controller import Controller

driver = Controller(debug = True).execute()
