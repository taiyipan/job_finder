import json
# retrieve credentials json data
class Credential:
    def __init__(self):
        self.credentials_path = '/home/taiyi/job_finder/credentials/credentials.json'
        self.credentials = self.load_credentials()

    def load_credentials(self):
        try:
            with open(self.credentials_path) as file:
                credentials = json.load(file)
            return credentials
        except:
            print('\nCredentials could not be located')

    def email_account(self) -> str:
        return self.credentials['email_account']

    def email_password(self) -> str:
        return self.credentials['email_password']

    def receiver_email(self) -> str:
        return self.credentials['receiver_email']

    def server_address(self) -> str:
        return self.credentials['server_address']
