from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from datetime import date
import platform
import time
import yagmail

# define search criteria
job_titles = [
    'junior software developer',
    'machine learning intern'
]
job_location = None
limit = 50
attempts = 3
headless = True

# open driver and browser
def find_driver_path() -> str:
    # set chromedriver path for local machine
    driver_path = '/usr/bin/chromedriver' # Ubuntu
    driver_path2 = '/mnt/c/Users/taiyi/taiyi/automata/1_twitter_bot/sign_up_bot/chromedriver.exe' # Windows 10
    driver_path3 = '/Users/taiyipan/chromedriver' # Mac OSX
    # get current host computer name
    hostname = platform.node()
    # return driver_path
    if hostname == 'Galatea':
        return driver_path2
    elif hostname == 'sol.lan':
        return driver_path3
    elif hostname == 'eternal' or hostname == 'raspberrypi':
        return driver_path
    else: # if host computer is not recognized
        driver.close()
        quit()
driver_path = find_driver_path()

# main loop
for job_title in job_titles:
    print('\nMining for newest "{}" jobs, limit at {}'.format(job_title, limit))
    # sub loop: attempts
    for i in range(attempts):
        # generate feature file name
        def feature_name() -> str:
            # validate criteria
            assert job_title is not None or job_location is not None or limit is not None, 'Error: search criteria too broad'
            # create file name string
            feature_name = 'data/features/'
            if job_title is not None:
                feature_name += job_title.replace(' ', '_')
            if job_location is not None:
                feature_name += job_location.replace(' ', '_')
            if job_title is None and job_location is None:
                feature_name += str(limit) + '_random'
            feature_name += '_' + str(date.today()) + '.txt'
            return feature_name
        feature_name = feature_name()

        # open data storage file
        output = open(feature_name, mode = 'w')

        # initialize error state
        error = False

        # configure chromedriver options
        options = Options()
        if headless:
            options.headless = True
            options.add_argument('--log-level=3')
            options.add_argument('--window-size=1920x1080')

        # open chromedriver
        driver = webdriver.Chrome(executable_path = driver_path, chrome_options = options)
        driver.maximize_window()

        # navigate to webpage
        driver.get('https://www.indeed.com')

        # enter 2 input fields on job search page
        if job_title is not None:
            input_what = driver.find_element_by_id('text-input-what')
            input_what.send_keys(job_title)

        input_where = driver.find_element_by_id('text-input-where')
        input_where.send_keys(Keys.CONTROL + 'a')
        input_where.send_keys(Keys.DELETE)

        if job_location is not None:
            input_where.send_keys(job_location)
        input_where.send_keys('\n')

        # refine search results on the left column in order (1: experience, 2: date)

        # (1) show only entry level positions
        try:
            select_experience = WebDriverWait(WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((
                    By.ID,
                    'refineresults'
                ))
            ), 5).until(
                EC.presence_of_element_located((
                    By.XPATH,
                    './/div[@id="rb_Experience Level"]/div[@id="EXP_LVL_rbo"]/ul[@class="rbList"]/li/a[contains(@title, "Entry Level")]'
                ))
            )
        except:
            select_experience = WebDriverWait(WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((
                    By.ID,
                    'filter-experience-level-menu'
                ))
            ), 5).until(
                EC.presence_of_element_located((
                    By.XPATH,
                    './/li/a[contains(@title, "Entry Level")]'
                ))
            )
        try:
            select_experience.click()
        except:
            driver.execute_script("arguments[0].click();", select_experience)

        # (2) sort results by date
        try:
            sort_by_date = WebDriverWait(WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((
                    By.ID,
                    'refineresults'
                ))
            ), 5).until(
                EC.presence_of_element_located((
                    By.XPATH,
                    './/div[@class="serp-filters-sort-by-container"]/span[@class="no-wrap"]/a[text()="date"]'
                ))
            )
        except:
            sort_by_date = WebDriverWait(WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((
                    By.ID,
                    'resultsCol'
                ))
            ), 5).until(
                EC.presence_of_element_located((
                    By.XPATH,
                    './/div[@class="resultsTop"]/div[@class="secondRow"]/div[@class="serp-filters-sort-by-container"]/span[@class="no-wrap"]/a[text()="date"]'
                ))
            )
        try:
            sort_by_date.click()
        except:
            driver.execute_script("arguments[0].click();", sort_by_date)

        # search loop
        count = 0
        last_page = 0
        while count < limit:
            # validate current page is after previous page (compensate for indeed website glitch)
            # if validated, update current page
            current_page = WebDriverWait(WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((
                    By.CLASS_NAME,
                    'pagination'
                ))
            ), 5).until(
                EC.presence_of_element_located((
                    By.XPATH,
                    './/b'
                ))
            )
            current_page = int(current_page.text)
            if current_page == last_page + 1:
                last_page = current_page
            else:
                print('Indeed page glitch detected.')
                error = True
                break

            # get all jobs on the current page
            jobs = WebDriverWait(WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((
                    By.ID,
                    'resultsCol'
                ))
            ), 10).until(
                EC.presence_of_all_elements_located((
                    By.CLASS_NAME,
                    'jobsearch-SerpJobCard'
                ))
            )

            # loop through current jobs
            for job in jobs:
                # write job card to file
                output.write(job.text + '\n\n')

                # get job title link
                job_title_link = WebDriverWait(job, 5).until(
                    EC.presence_of_element_located((
                        By.XPATH,
                        './/h2[@class="title"]/a'
                    ))
                )

                # click on job title and expand job description
                try:
                    job_title_link.click()
                except:
                    driver.execute_script("arguments[0].click();", job_title_link)

                try:
                    # get job description
                    description = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((
                            By.ID,
                            'vjs-desc'
                        ))
                    )
                    # write job description to file
                    output.write(description.text + '\n\n')
                except:
                    try:
                        # get job description
                        description = WebDriverWait(driver, 5).until(
                            EC.presence_of_element_located((
                                By.ID,
                                'jobDescriptionText'
                            ))
                        )
                        # write job description to file
                        output.write(description.text + '\n\n')
                    except:
                        pass

                # write entry seperation tag to file
                output.write('<<END>>\n\n')

                # update job count
                count += 1
                if count % 100 == 0:
                    print('{} entries'.format(count))
                if count == limit:
                    print('limit at {} reached'.format(limit))
                    break

            # locate next button
            try:
                next = WebDriverWait(driver, 3).until(
                    EC.presence_of_element_located((
                        By.LINK_TEXT,
                        'Next »'
                    ))
                )
            except:
                try:
                    next = WebDriverWait(WebDriverWait(driver, 3).until(
                        EC.presence_of_element_located((
                            By.ID,
                            'resultsCol'
                        ))
                    ), 3).until(
                        EC.presence_of_element_located((
                            By.XPATH,
                            './/nav[@role="navigation"]/div[@class="pagination"]/ul[@class="pagination-list"]/li/a[@aria-label="Next"]'
                        ))
                    )
                except Exception as e:
                    print(e)
                    print('Next not detected')
                    break
            # go to next page
            try:
                next.click()
            except:
                driver.execute_script("arguments[0].click();", next)

        # close data storage file
        output.close()
        # close driver
        driver.quit()

        # harvest summary
        print('\nHarvested {} job postings for job "{}"'.format(count, job_title))

        # handle website glitch
        if error:
            print('\nDue to website glitch, making another attempt')
            # wait a moment
            time.sleep(10)
        else:
            break

# send email report
report = str()
report += '\nHello Taiyi! This is your Data Miner A.I. program.'
report += '\nI mined a bunch of new jobs today.'
report += '\nJob titles: ' + str(job_titles)
report += '\nIf you have time, please label them. Thanks!'

email_account = ''
email_password = ''
receiver_email = ''
yag = yagmail.SMTP(email_account, email_password)
yag.send(to = receiver_email, subject = 'Data Miner Completed', contents = report)
