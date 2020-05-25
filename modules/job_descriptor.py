from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
# get job description web element, extract its text
class JobDescriptor:
    def __init__(self, driver, wait_time):
        self.driver = driver
        self.wait_time = wait_time

    def method_1(self):
        description = WebDriverWait(self.driver, self.wait_time).until(
            EC.presence_of_element_located((
                By.ID,
                'vjs-desc'
            ))
        )
        return description.text

    def method_2(self):
        description = WebDriverWait(self.driver, self.wait_time).until(
            EC.presence_of_element_located((
                By.ID,
                'jobDescriptionText'
            ))
        )
        return description.text

    def method_3(self):
        # switch to iframe vjs-container-iframe
        self.driver.switch_to_frame('vjs-container-iframe')
        # get element within iframe
        description = self.method_2()
        # switch back to default content
        self.driver.switch_to_default_content()
        # return element
        return str(description)
