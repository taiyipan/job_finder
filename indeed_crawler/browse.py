from __future__ import absolute_import, division, print_function, unicode_literals
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # suppress tensorflow messages
import tensorflow as tf
from tensorflow import keras
import numpy as np
import time
from tensorflow_serving.apis.predict_pb2 import PredictRequest
import grpc
from tensorflow_serving.apis import prediction_service_pb2_grpc
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from datetime import datetime
from datetime import timedelta
import platform
import operator
import yagmail

# define search criteria
job_title = None
job_location = 'San Francisco Bay Area'
limit = 2000
confidence_threshold = 0.9
attempts = 3
duration = 45 # minutes
debug = False

# start timer
timer = time.time()
# calculate a fixed end time in the future
end = datetime.now() + timedelta(minutes = duration)

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

# initialize email report content
email_account = ''
email_password = ''
receiver_email = ''
yag = yagmail.SMTP(email_account, email_password)
report = str()
report += '\nHello Taiyi! This is your Job Finder A.I. program.'

# main loop
for i in range(attempts):
    print('\nAttempting to harvest today\'s jobs')
    print('Job title: {}'.format(job_title))
    print('Job location: {}'.format(job_location))
    print('Entry harvest limit: {} entries'.format(limit))
    print('Runtime duration limit: {} minutes'.format(duration))
    print('AI prediction confidence threshold: {}'.format(confidence_threshold))
    print('Debug mode: {}\n'.format(debug))

    # initialize error state
    error = False

    # configure chromedriver options
    options = Options()
    if not debug:
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

    # refine search results on the left column in order (1: distance, 2: experience, 3: date)

    # (1) specify distance to 50 miles
    try:
        select_distance = WebDriverWait(WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((
                By.ID,
                'distance_selector'
            ))
        ), 5).until(
            EC.presence_of_element_located((
                By.XPATH,
                './/option[text()="within 50 miles"]'
            ))
        )
    except:
        select_distance = WebDriverWait(WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((
                By.ID,
                'filter-distance-menu'
            ))
        ), 5).until(
            EC.presence_of_element_located((
                By.XPATH,
                './/li/a[contains(@title, "within 50 miles")]'
            ))
        )
    try:
        select_distance.click()
    except:
        driver.execute_script("arguments[0].click();", select_distance)

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

    # (3) sort results by date
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
    input_data = list() # X input to be fed into neural net on a remote server
    summaries = list() # store job summary info
    links = list() # store job links
    count = 0
    last_page = 0
    today = True
    desc_mode = 1 # initialize mode
    next_mode = 1 # initialize mode
    while count < limit and today:
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

        # validate program does not exceed program duration
        if datetime.now() > end:
            print('Program exceeded duration of {} minutes, so exiting'.format(duration))
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
            # validate the job is still posted today
            job_date = WebDriverWait(job, 5).until(
                EC.presence_of_element_located((
                    By.XPATH,
                    './/div[@class="jobsearch-SerpJobCard-footer"]'
                ))
            )
            if '1 day ago' in job_date.text:
                today = False
                print('Reached yesterday\'s posting')
                break

            # initialize input_string and save job text
            input_string = str()
            input_string += job.text + '\n\n'

            # save job summary
            summaries.append(job.text)

            # find and save job link
            links.append(
                WebDriverWait(job, 5).until(
                    EC.presence_of_element_located((
                        By.XPATH,
                        './/h2[@class="title"]/a'
                    ))
                ).get_attribute('href')
            )

            # get job title
            job_title = WebDriverWait(job, 5).until(
                EC.presence_of_element_located((
                    By.XPATH,
                    './/h2[@class="title"]/a'
                ))
            )

            # click on job title and expand job description
            try:
                job_title.click()
            except:
                driver.execute_script("arguments[0].click();", job_title)

            # get job description: 2 modes for time optimization
            if desc_mode == 1:
                try:
                    description = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((
                            By.ID,
                            'vjs-desc'
                        ))
                    )
                    # save job description
                    input_string += description.text + '\n\n'
                except:
                    try:
                        description = WebDriverWait(driver, 5).until(
                            EC.presence_of_element_located((
                                By.ID,
                                'jobDescriptionText'
                            ))
                        )
                        # save job description
                        input_string += description.text + '\n\n'
                        # change mode
                        desc_mode = 2
                    except:
                        pass
            elif desc_mode == 2:
                try:
                    description = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((
                            By.ID,
                            'jobDescriptionText'
                        ))
                    )
                    # save job description
                    input_string += description.text + '\n\n'
                except:
                    try:
                        description = WebDriverWait(driver, 5).until(
                            EC.presence_of_element_located((
                                By.ID,
                                'vjs-desc'
                            ))
                        )
                        # save job description
                        input_string += description.text + '\n\n'
                        # change mode
                        desc_mode = 1
                    except:
                        pass

            # save input_string to input_data
            input_data.append(input_string)

            # update job count
            count += 1
            if count % 100 == 0:
                print('{} entries'.format(count))
            if count == limit:
                print('limit at {} reached'.format(limit))
                break

        # locate next button: 2 modes for time optimization
        if next_mode == 1:
            try:
                next = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((
                        By.LINK_TEXT,
                        'Next »'
                    ))
                )
            except:
                try:
                    next = WebDriverWait(WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((
                            By.ID,
                            'resultsCol'
                        ))
                    ), 5).until(
                        EC.presence_of_element_located((
                            By.XPATH,
                            './/nav[@role="navigation"]/div[@class="pagination"]/ul[@class="pagination-list"]/li/a[@aria-label="Next"]'
                        ))
                    )
                    # change mode
                    next_mode = 2
                except Exception as e:
                    print(e)
                    print('Next not detected')
                    break
        elif next_mode == 2:
            try:
                next = WebDriverWait(WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((
                        By.ID,
                        'resultsCol'
                    ))
                ), 5).until(
                    EC.presence_of_element_located((
                        By.XPATH,
                        './/nav[@role="navigation"]/div[@class="pagination"]/ul[@class="pagination-list"]/li/a[@aria-label="Next"]'
                    ))
                )
            except:
                try:
                    next = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((
                            By.LINK_TEXT,
                            'Next »'
                        ))
                    )
                    # change mode
                    next_mode = 1
                except Exception as e:
                    print(e)
                    print('Next not detected')
                    break

        # go to next page
        try:
            next.click()
        except:
            driver.execute_script("arguments[0].click();", next)

    # close driver and all windows
    if not debug:
        driver.quit()

    # harvest summary
    print('\nHarvested {} job postings from today'.format(len(input_data)))

    # handle website glitch
    if error:
        print('\nDue to website glitch, making another attempt')
        # wait a moment
        time.sleep(10)
    else:
        break

# handle empty input_data
if len(input_data) == 0:
    print('\nNo data harvested. Ending program.')
    # send email report
    report += '\nUnfortunately, no data was harvested this time.'
    yag.send(to = receiver_email, subject = 'Zero Data Harvested', contents = report)
    quit()

# prepare query
request = PredictRequest()
request.model_spec.name = 'job_finder'
request.model_spec.signature_name = 'serving_default'
input_name = 'keras_layer_input'
output_name = 'dense_4'
request.inputs[input_name].CopyFrom(tf.make_tensor_proto(tf.convert_to_tensor(input_data, dtype = tf.string)))

# send query
try:
    server_address = ''
    print('\nSending input data to remote tensorflow server at {}'.format(server_address))
    channel = grpc.insecure_channel(server_address)
    predict_service = prediction_service_pb2_grpc.PredictionServiceStub(channel)
    response = predict_service.Predict(request, timeout = 60.0)
    print('Response from remote server received')
except:
    # if tensorflow server isn't responding, send error report through email and quit program
    print('\nRemote tensorflow server not responding')
    # send email report
    report += '\nUnfortunately, remote tensorflow server was not responding.'
    yag.send(to = receiver_email, subject = 'Tensorflow Server Unresponsive', contents = report)
    quit()

# process response
output_proto = response.outputs[output_name]
output = np.squeeze(tf.make_ndarray(output_proto))
print('\nObtained {} results'.format(len(output)))

# perform analytics
positives = (output > confidence_threshold).nonzero()[0]
print('\nDetected {} positives'.format(len(positives)))

# compile results for output
results = list()
for pos in positives:
    results.append((output[pos], summaries[pos], links[pos]))
# sort results based on confidence level in descending order
results = sorted(results, key = operator.itemgetter(0), reverse = True)

# stop timer and record time elapsed in minutes
duration = round((time.time() - timer) / 60)

# compose report into 1 long string
report += '\nI found {} new jobs, and selected {} possibly good ones for you.'.format(len(output), len(results))
report += '\n\nReport time: {}'.format(datetime.now().strftime('%A, %b %-d %Y, %-I:%-M%p'))
report += '\nProgram runtime duration: {} minutes'.format(duration)
report += '\n\nResults below sorted by confidence level, from high to low\n'
for i in range(len(results)):
    report += '\n\nEntry {}'.format(i + 1)
    report += '\nConfidence level: {:.4f}'.format(results[i][0])
    for k in range(1, len(results[i])):
        report += '\n' + results[i][k]
print(report)

# send final report through email
if not debug:
    yag.send(to = receiver_email, subject = 'Job Finder Successful', contents = report)
    print('\nEmail report sent to {}'.format(receiver_email))

# store results to history
if not debug:
    history_path = '/home/taiyi/job_finder/indeed_crawler/trends/history.csv' # absolute path because script initiated from cron daemon
    try:
        with open(history_path, 'a') as history:
            entry = datetime.now().strftime('%A_%b-%-d-%Y_%-I:%-M%p')
            entry += ',' + str(len(output)) + ',' + str(len(results)) + ','
            entry += '{:.1f}%'.format(len(results) / len(output) * 100) + '\n'
            history.write(entry)
            print('\nResults saved to {}'.format(history_path))
    except Exception as e:
        print()
        print(e)
        print('\n{} cannot be appended'.format(history_path))

# terminate program
quit()
