import sys
sys.path.insert(0, '/home/taiyi/job_finder/modules/')
from miner import Miner

job_titles = [

]

miner = Miner(mode = 'negative mine', debug = True)
miner.mine(job_titles)
