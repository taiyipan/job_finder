from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import date
import platform
import time

# define search criteria
job_title = 'junior machine learning engineer'
job_location = None
limit = 2000

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

driver = webdriver.Chrome(executable_path = driver_path)
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

# start timer
timer = time.time()

# search loop
count = 0
last_page = 0
while count < limit:
    # validate current page is after previous page (compensate for indeed website glitch)
    # if validated, update current page
    pages = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((
            By.CLASS_NAME,
            'pagination'
        ))
    )
    current_page = WebDriverWait(pages, 10).until(
        EC.presence_of_element_located((
            By.XPATH,
            './/b'
        ))
    )
    current_page = int(current_page.text)
    if current_page == last_page + 1:
        last_page = current_page
    else:
        print('Indeed page glitch detected. Aborting program.')
        break

    # get all jobs on the current page
    jobs = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((
            By.CLASS_NAME,
            'jobsearch-SerpJobCard'
        ))
    )

    # loop through current jobs
    for job in jobs:
        # write job card to file
        output.write(job.text + '\n\n')

        # try to click job card
        try:
            job.click()
        except:
            # click via JavaScript (bypass popup block)
            driver.execute_script("arguments[0].click();", job)
            # print('Bypass job card click block')
            pass

        # dynamic job description harvest
        # program will continue even if both attempts fail
        try:
            # get job description
            description = WebDriverWait(driver, 3).until(
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
                description = WebDriverWait(driver, 3).until(
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
        increment = 100
        if count % increment == 0:
            # update timer
            print('{} samples mined at speed: {:.2f} second/sample'.format(count, (time.time() - timer) / increment))
            timer = time.time()
        if count == limit:
            print('\n{} limit reached, stopping\n'.format(limit))
            break

    # try to locate "next" button
    try:
        next = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((
                By.LINK_TEXT,
                'Next »'
            ))
        )
    except:
        print('All jobs for search terms \"' + job_title + '\" exhausted')
        break

    # try to click "next"
    try:
        next.click()
    except:
        # click via JavaScript (bypass popup block)
        driver.execute_script("arguments[0].click();", next)
        # print('Bypass next button click block')
        pass

# close data storage file
output.close()
# close driver
driver.close()

# <span class="np">«&nbsp;Previous</span>
# <span class="np">Next&nbsp;»</span>
