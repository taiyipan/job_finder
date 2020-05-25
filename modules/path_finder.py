import platform
# find driver path for the local machine hosting the process
class PathFinder:
    # constructor
    def __init__(self):
        # define driver paths for various machines
        self.driver_path = '/usr/bin/chromedriver' # Ubuntu
        self.driver_path2 = '/mnt/c/Users/taiyi/taiyi/automata/1_twitter_bot/sign_up_bot/chromedriver.exe' # Windows 10
        self.driver_path3 = '/Users/taiyipan/chromedriver' # Mac OSX

    # return chromedriver path on local machine 
    def find_driver_path(self):
        # get current host computer name
        hostname = platform.node()
        # return driver_path
        if hostname == 'Galatea':
            return self.driver_path2
        elif hostname == 'sol.lan':
            return self.driver_path3
        elif hostname == 'eternal' or hostname == 'raspberrypi':
            return self.driver_path
        else:
            return None
