import sys
sys.path.insert(0, '/home/taiyi/job_finder/modules/')
from controller import Controller

driver = Controller(
    job_title = 'python developer',
    job_location = None,
    debug = True,
    limit = 200,
    distance = False,
    date_limit = False
).execute()
