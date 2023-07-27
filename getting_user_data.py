import requests
import json
from datetime import datetime, timedelta
import time
from tqdm import tqdm
import csv


class IndiaMartScraper:

    def __init__(self, credentials):
        self.url = 'https://seller.indiamart.com/enquiry/messagecentre/GetUserContacts'
        self.headers = {
            'authority': 'seller.indiamart.com',
            'accept': 'application/json, text/javascript, /; q=0.01',
            'accept-language': 'en-US,en;q=0.9',
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'cookie': credentials['cookie'],
            'origin': 'https://seller.indiamart.com',
            'referer': 'https://seller.indiamart.com/enquiry/messagecentre?lv=1',
            'sec-ch-ua': '"Not/A)Brand";v="99", "Google Chrome";v="115", "Chromium";v="115"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': 'Windows',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
            'x-requested-with': 'XMLHttpRequest',
        }
        self.seen_users = self.load_seen_users()
        self.user_list = list(self.seen_users)
        self.glid = credentials['glid']
        self.loginglid = credentials['loginglid']

    @staticmethod
    def load_seen_users():
        """Load seen users from existing JSON file, or return an empty set if file does not exist."""
        try:
            with open("data.json", 'r') as file:
                all_data = json.load(file)
                return {(user['contactglid'], user['imcontactid'], user['mobile']) for user in all_data}
        except FileNotFoundError:
            return set()

    def get_data(self, start, end, value):
        """Send a post request and process the response."""
        data = {
            'glid': self.glid,
            'type': '0',
            'start': str(start),
            'end': str(end),
            'last_contact_date': value.strftime('%Y-%m-%d %H:%M:%S')  # Convert the datetime to a string
        }


        response = requests.post(self.url, headers=self.headers, data=data)

        if response.ok:
            self.process_response(response.json())
        else:
            print(f"Request failed with status code: {response.status_code}, data: {data}")

    def process_response(self, json_data):
        """Process the response JSON data."""

        if json_data is not None:
            for user_data in json_data.get('result', []):
                try:
                    user_id = (user_data['contacts_glid'], user_data['im_contact_id'], user_data['contacts_mobile1'])
                    if user_id not in self.seen_users:
                        new_user = {
                            "mobile": user_data['contacts_mobile1'],
                            'requirement': user_data['contact_last_product'],
                            'name': user_data['contacts_name'],
                            'city': user_data['contact_city'],
                            'state': user_data['contact_state'],
                            'company': user_data['contacts_company'],
                            'lead_available_from': user_data['contacts_add_date']
                        }

                        self.user_list.append(new_user)
                        self.seen_users.add(user_id)
                except KeyError as e:
                    print(f"Error processing data, missing key: {str(e)}")
                except Exception as e:
                    print(f"Error processing data: {str(e)}")
        else:
            print(f"Error processing data: {json_data['code']}")

    def save_data(self):
        """Save user list data to a JSON file."""
        with open('data.json', 'w') as f:
            json.dump(self.user_list, f)

        headers = self.user_list[0].keys()

        with open('indiamart_leads.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=headers)  # Use keys as fieldnames
            writer.writeheader()  # Write headers to CSV file
            writer.writerows(self.user_list)  # Write data to CSV file

    def run(self):
        """Main script logic."""
        # Initialize the date value
        value = datetime(2023, 7, 23, 0, 0, 0)

        for i in tqdm(range(1, 2)):  # Iterate over search entries of 50 users ; Change as per requirement
            time.sleep(7)
            start = i * 50 + 1  # start at 1, 51
            end = (i + 1) * 50  # end at 50, 100
            for _ in tqdm(range(15)):  # Iterate over a 30-day period; Change as per requirement
                time.sleep(0.5)
                self.get_data(start, end, value)

                # After each day, decrement value by 1 day
                value -= timedelta(days=1)

        self.save_data()


if __name__ == '__main__':
    with open('credentials.json', 'r') as file:
        credentials = json.load(file)
    scraper = IndiaMartScraper(credentials)
    scraper.run()