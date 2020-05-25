from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from path_finder import PathFinder
# create and return chromedriver object
class DriverInitializer:
    # constructor
    def __init__(self, debug = False):
        # configure chromedriver options
        options = Options()
        if not debug:
            options.headless = True
            options.add_argument('--log-level=3')
            options.add_argument('--window-size=1920x1080')

        # find driver path
        path_finder = PathFinder()
        driver_path = path_finder.find_driver_path()

        # open chromedriver
        self.driver = webdriver.Chrome(executable_path = driver_path, chrome_options = options)
        self.driver.maximize_window()

    # return chromedriver object reference
    def get_driver(self):
        return self.driver
