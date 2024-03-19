import re
import logging
import json

from selector import select as se
from parsel import Selector
from requests import Session
from requests.exceptions import ConnectionError, ConnectTimeout


class Scraper(Session):
    def __init__(self):
        super().__init__()
        self.headers.update({'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537 (KHTML, like Gecko)'})

    @staticmethod
    def decode_email(encoded_email):
        decoded_email = ''
        for char in encoded_email:
            code = ord(char)
            if 97 <= code <= 122:  # Lowercase letters
                code = 97 + ((code - 84) % 26)
            elif 65 <= code <= 90:  # Uppercase letters
                code = 65 + ((code - 52) % 26)
            decoded_email += chr(code)
        return decoded_email.replace('A', '.').replace('N', '@')

    @staticmethod
    def export_data(name: str, data: list[dict]) -> None:
        with open(f'{name}.json', 'w', encoding='utf-8') as export_file:
            json.dump(data, export_file)

    def get_links(self):
        req_response = self.get('https://www.txcumc.org/wp-admin/admin-ajax.php?action=get_churches_br&env=frontend&nonce=66fc090413').json()
        return [
            'https://www.txcumc.org' + link[0].split('href="')[1].split('">')[0]
            for link in req_response
        ]

    def scrape(self, response: Selector) -> dict[str, str]:
        church_details = {
                "name": response.css(se['church_name']).extract_first(),
                "phone": re.sub(r'[)(-]', '', response.css(se['phone']).extract_first() or '').replace(' ', '')
        }

        clergy_link = 'https://www.txcumc.org' + link if '/clergy-directory/' in (link := response.css(se['clergy_link']).get() or '') else ''
        if clergy_link:
            info = Selector(self.get(clergy_link).text, type='html')
            church_details["email"] = self.decode_email((info.css(se['email']).get() or '').split('=')[-1])
            church_details["clergy_name"] = info.css(se['clergy_name']).extract_first()

        address_info = ["address", "city", "state"]
        full_address = ','.join(response.css(se['physical_address']).extract()).replace(',,', ',').split(',')
        for address in full_address:
            if full_address.index(address)+1 > len(address_info): break
            info = address_info[full_address.index(address)]
            church_details[info] = address.strip()

        zip_code = response.css(se['physical_address']).extract() or response.css(se['mailing_address']).extract()
        if zip_code: church_details['zip_code'] = zip_code[-1].split(',')[-1].strip()
        else: church_details['zip_code'] = ''

        return church_details


def scrape_church(church_url: str):
    try: request = scraper.get(church_url).text
    except (ConnectionError, ConnectTimeout) as e:
        logging.error(f'{e} while scraping from {church_url} retrying')
        scrape_church(church_url)
    else:
        request = Selector(request, type='html')
        data = scraper.scrape(request)

        print(data)
        data_list.append(data)


if __name__ == '__main__':
    data_list = []
    logging.basicConfig(level=logging.INFO, filemode='w', format='%(asctime)s-%(levelname)s- %(message)s', filename='txcumc.log')

    scraper = Scraper()
    links = scraper.get_links()
    for church_link in links:
        scrape_church(church_link)

    scraper.export_data('txcumc', data_list)
