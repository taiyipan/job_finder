import sys
sys.path.insert(0, '/home/taiyi/job_finder/modules/')
from miner import Miner

job_titles = [
    'python developer',
    'machine learning intern'
]

miner = Miner(mode = 'mine', debug = True)
miner.mine(job_titles)
