from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class ExperienceSelector:
    def __init__(self, driver, wait_time, experience):
        self.driver = driver
        self.wait_time = wait_time
        self.experience = experience

    def method_1(self):
        select_experience = WebDriverWait(WebDriverWait(self.driver, self.wait_time).until(
            EC.presence_of_element_located((
                By.ID,
                'filter-experience-level-menu'
            ))
        ), self.wait_time).until(
            EC.presence_of_element_located((
                By.XPATH,
                './/li/a[contains(@title, "{}")]'.format(self.experience)
            ))
        )
        return select_experience

    def method_2(self):
        select_experience = WebDriverWait(WebDriverWait(self.driver, self.wait_time).until(
            EC.presence_of_element_located((
                By.ID,
                'refineresults'
            ))
        ), self.wait_time).until(
            EC.presence_of_element_located((
                By.XPATH,
                './/div[@id="rb_Experience Level"]/div[@id="EXP_LVL_rbo"]/ul[@class="rbList"]/li/a[contains(@title, "{}")]'.format(self.experience)
            ))
        )
        return select_experience

    def method_3(self):
        select_experience = WebDriverWait(WebDriverWait(self.driver, self.wait_time).until(
            EC.presence_of_element_located((
                By.ID,
                'filter-experience-level-menu'
            ))
        ), self.wait_time).until(
            EC.presence_of_element_located((
                By.XPATH,
                './/li/a/span[contains(text(), "{}")]'.format(self.experience)
            ))
        )
        return select_experience
