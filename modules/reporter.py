import numpy as np
import yagmail
import operator
from datetime import datetime
from credential import Credential
# interpret query results, send email report, and log results to history
class Reporter:
    def __init__(self):
        self.history_path = '/home/taiyi/job_finder/indeed_crawler/trends/history.csv'

    def report(self, output, summaries, links, duration, confidence_threshold):
        if output is None:
            self.fail()
        # get positives
        positives = self.positives(output, confidence_threshold)
        # get results
        results = self.results(output, positives, summaries, links)
        # compose message
        message = self.message(output, results, duration)
        # send message
        self.send(message)
        # log search results
        self.log(output, results)

    def fail(self):
        self.send('Tensorflow server query failed', 'Failure')
        quit()

    def positives(self, output, confidence_threshold):
        # perform analytics
        positives = (output > confidence_threshold).nonzero()[0]
        print('\nDetected {} positives'.format(len(positives)))
        return positives

    def results(self, output, positives, summaries, links):
        # compile results
        results = list()
        for pos in positives:
            results.append((output[pos], summaries[pos], links[pos]))
        # sort results based on confidence level in descending order
        results = sorted(results, key = operator.itemgetter(0), reverse = True)
        return results

    def message(self, output, results, duration) -> str:
        message = str()
        message += '\nHello Taiyi! This is your Job Finder A.I. program.'
        message += '\nI found {} new jobs, and selected {} possibly good ones for you.'.format(len(output), len(results))
        message += '\n\nReport time: {}'.format(datetime.now().strftime('%A, %b %-d %Y, %-I:%-M%p'))
        message += '\nProgram runtime duration: {} minutes'.format(duration)
        message += '\n\nResults below sorted by confidence level, from high to low\n'
        for i in range(len(results)):
            message += '\n\nEntry {}'.format(i + 1)
            message += '\nConfidence level: {:.4f}'.format(results[i][0])
            for k in range(1, len(results[i])):
                message += '\n' + results[i][k]
        print(message)
        return message

    def send(self, message: str, subject = 'Job Finder Report'):
        # load credentials
        credentials = Credential()
        # send email
        yag = yagmail.SMTP(
            credentials.email_account(),
            credentials.email_password()
        )
        yag.send(
            to = credentials.receiver_email(),
            subject = subject,
            contents = message
        )
        print('\nEmail report sent to {}'.format(credentials.receiver_email()))

    # store results to history
    def log(self, output, results):
        try:
            with open(self.history_path, 'a') as history:
                entry = datetime.now().strftime('%A_%b-%-d-%Y_%I:%M%p')
                entry += ',' + str(len(output)) + ',' + str(len(results)) + ','
                entry += '{:.1f}%'.format(len(results) / len(output) * 100) + '\n'
                history.write(entry)
                print('\nResults saved to {}'.format(self.history_path))
        except Exception as e:
            print()
            print(e)
            print('\n{} cannot be appended'.format(self.history_path))
