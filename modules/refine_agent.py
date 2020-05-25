from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from adaptive_recursor import AdaptiveRecursor
from distance_selector import DistanceSelector
from experience_selector import ExperienceSelector
from date_selector import DateSelector
from clicker import Clicker
# refine search based on certain conditions
class RefineAgent:
    # constructor
    def __init__(self, driver, distance = 'within 50 miles', experience = 'Entry Level', order_by_date = True, wait_time = 5):
        self.driver = driver
        self.distance = distance
        self.experience = experience
        self.order_by_date = order_by_date
        self.wait_time = wait_time

    # refine search results
    def refine(self):
        if self.distance:
            self.select_distance()
        if self.experience:
            self.select_experience()
        if self.order_by_date:
            self.select_date()

    # refine results by distance
    def select_distance(self):
        Clicker(self.driver, AdaptiveRecursor(DistanceSelector(self.driver, self.wait_time, self.distance)).get()).click()

    # refine results by experience
    def select_experience(self):
        Clicker(self.driver, AdaptiveRecursor(ExperienceSelector(self.driver, self.wait_time, self.experience)).get()).click()

    # sort results by date (newest to oldest)
    def select_date(self):
        Clicker(self.driver, AdaptiveRecursor(DateSelector(self.driver, self.wait_time)).get()).click()
