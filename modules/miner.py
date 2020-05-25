from controller import Controller
from datetime import date

class Miner:
    def __init__(self, mode: str, debug: bool):
        self.mode = mode
        self.debug = debug

    def mine(self, job_titles: list(), limit = 500):
        for job_title in job_titles:
            controller = Controller(
                job_title = job_title,
                job_location = None,
                distance = False,
                limit = limit,
                debug = self.debug,
                mode = self.mode,
                date_limit = False,
                feature_path = self.make_feature_path(mode = self.mode, job_title = job_title, job_location = None, limit = limit)
            )
            driver = controller.execute()

    def make_feature_path(self, mode: str, job_title: str, job_location: str, limit: int) -> str:
        # validate criteria
        assert job_title is not None or job_location is not None or limit is not None, 'Error: search criteria too broad'
        # create file name string
        if mode == 'mine':
            feature_name = '/home/taiyi/job_finder/data_miner/data/features/'
        elif mode == 'negative mine':
            feature_name = '/home/taiyi/job_finder/data_miner/false_data/features/'
        if job_title is not None:
            feature_name += job_title.replace(' ', '_')
        if job_location is not None:
            feature_name += job_location.replace(' ', '_')
        if job_title is None and job_location is None:
            feature_name += str(limit) + '_random'
        feature_name += '_' + str(date.today()) + '.txt'
        return feature_name
