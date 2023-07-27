Sure, here's a basic README structure that you can use for your project:

---

# IndiaMart Scraper

This is a Python-based scraping tool designed to extract user contacts from IndiaMart. The scraper uses an unofficial IndiaMart API to retrieve data and saves it in JSON and CSV formats.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine.

### Prerequisites

You will need the following Python packages installed on your local machine:
* requests
* json
* datetime
* time
* tqdm
* csv

Use `pip requirements.txt` to install the requirements 

### Usage

1. Update the `credentials.json` file with your IndiaMart credentials. You will need the following information:

- `cookie` 
- `glid`
- `loginglid`

As mentioned in the following images, you will be able to extract the cookies from the GetUserContact network call

The glid and the loginglid will most likely be the same and you can find that as part of the sample payload when sending a GetUserContact POST request to Indiamart at `https://seller.indiamart.com/enquiry/messagecentre/GetUserContacts`

2. Run the script:
```
python IndiaMartScraper.py
```

## Functionality

* The way IndiaMart's user list works is similar to a product catalogue like that of Amazon. A page shows about 50 leads at once,
and there is an option to move to the next page via clicking the next button. 

* The first 50 leads are extracted by a simple POST request to the aforementioned URL with a simple body, but the subsequent entries (51-100, 101-150 ...)
are actually bound by a dynamic field in the body called "last_contact_date" which is equal to the timestamp of your 100th lead, 150th lead and so on.
Since it is impossilbe to figure out that, I ran a simple for loop to pass 15 different "last_contact_date" and get as much data as possible,
and then place a check for duplicate entries.

* For example, it's possible that for your use case, when you are extracting the data from 51 to 100th lead,
the Last contact date of your 80th lead is 10th July and that of your 90th lead is 8th July. So in the inner for loop within the getting_user_data.py file,
when the last contact date is set to 10th July, I will fetch user details from 50th to 80th rank. If it is 8th July, I will fetch from 50th to 90th Rank and so on

* In case you want only the first 50 leads, remove the last contact date from the payload

* The output will be stored in two files, data.json (as a json) and indiamart_leads.csv (as a csv).

* Indiamart cookies expire every 24 hours, so make sure to update it if you want to refresh your leads

* The current output stores the following items:
*                           'mobile': "845xxxxxxxx",
                            'requirement': "Resting Chair with 3 axis....",
                            'name': "John Doe",
                            'city': "Kolkata",
                            'state': "West Bengal",
                            'company': "Resters Pvt. Ltd.,
                            'lead_available_from': "12th July 2023 10:00:00"

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.

---

