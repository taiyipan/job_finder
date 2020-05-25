from driver_initializer import DriverInitializer
from login_agent import LoginAgent
from refine_agent import RefineAgent
from page_looper import PageLooper
from oracle import Oracle
from reporter import Reporter
import time

class Controller:
    def __init__(
        self,
        job_title = None,
        job_location = 'San Francisco Bay Area',
        limit = 2000,
        confidence_threshold = 0.9,
        duration = 40,
        debug = False,
        distance = 'within 50 miles',
        experience = 'Entry Level',
        order_by_date = True,
        date_limit = True,
        mode = 'browse',
        feature_path = None
    ):
        self.job_title = job_title
        self.job_location = job_location
        self.limit = limit
        self.confidence_threshold = confidence_threshold
        self.duration = duration
        self.debug = debug
        self.distance = distance
        self.experience = experience
        self.order_by_date = order_by_date
        self.date_limit = date_limit
        self.mode = mode
        self.feature_path = feature_path
        self.timer = time.time()

    def output_params(self):
        print('\nAttempting to harvest today\'s jobs')
        print('Job title: {}'.format(self.job_title))
        print('Job location: {}'.format(self.job_location))
        print('Entry harvest limit: {} entries'.format(self.limit))
        print('Runtime duration limit: {} minutes'.format(self.duration))
        print('AI prediction confidence threshold: {}'.format(self.confidence_threshold))
        print('Debug mode: {}\n'.format(self.debug))

    def execute(self):
        # display controller parameters
        self.output_params()

        # initialize driver
        initializer = DriverInitializer(debug = self.debug)
        driver = initializer.get_driver()

        # login and refine research
        login_agent = LoginAgent(driver, job_title = self.job_title, job_location = self.job_location)
        login_agent.login()
        refine_agent = RefineAgent(driver, distance = self.distance, experience = self.experience, order_by_date = self.order_by_date)
        refine_agent.refine()

        # create PageLooper object
        looper = PageLooper(driver, limit = self.limit, duration = self.duration, date_limit = self.date_limit)
        result = looper.loop()

        # close driver and all windows
        if not self.debug:
            driver.quit()

        # get data from PageLooper object
        input_data, summaries, links = looper.get_all()

        if self.mode == 'browse':
            # use oracle to process input_data
            oracle = Oracle()
            output = oracle.query(input_data)

            # stop timer and record time elapsed in minutes
            runtime_duration = round((time.time() - self.timer) / 60)

            # use reporter to process output
            reporter = Reporter()
            reporter.report(output, summaries, links, runtime_duration, self.confidence_threshold)

        else:
            # save input_data
            with open(self.feature_path, 'w') as output:
                for entry in input_data:
                    output.write(entry)
                    output.write('<<END>>\n\n')

        # return driver
        return driver

















#
