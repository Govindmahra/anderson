import logging
import json
import re
import time

from selector import select2 as se
from parsel import Selector
from requests import Session
from requests.exceptions import ConnectionError, ConnectTimeout


class Scraper(Session):
    def __init__(self):
        super().__init__()
        self.headers.update({'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537 (KHTML, like Gecko)'})

    @staticmethod
    def export_data(name: str, data: list[dict]) -> None:
        with open(f'{name}.json', 'w', encoding='utf-8') as export_file:
            export_file.write(json.dumps(data))

    def get_links(self) -> list[str]:
        churches = []

        req_response = self.get('https://www.nonprofitlist.org/TexasNonProfits.html').text
        selector = Selector(req_response, type='html')

        urls = [url for url in selector.css(se['link']).getall() if '/TX/' in url]
        for county_url in urls:
            try:response = self.get(county_url).text
            except (ConnectionError, ConnectTimeout):
                logging.error(f'error while scraping from {county_url}')
                continue
            churches += [url for url in Selector(response, type='html').css(se['church_url']).getall()]

        return churches

    @staticmethod
    def scrape(response: Selector) -> dict[str, str]:
        details = {
            "name": response.css(se['church_name']).extract_first(),
            "website": response.css(se['church_website']).get() or '',
            "phone": re.sub(r'[)(-]', '', response.css(se['church_phone']).extract_first() or '').replace(' ', '')
        }
        details["phone"] = details["phone"] if details["phone"].isdigit() else ''

        full_address = ','.join(response.css(se['church_address']).extract()).replace('\n', ' ').strip().split(',')
        address_info = ["city", "state", "zip_code"]
        for address in full_address:
            if full_address.index(address) + 1 > len(address_info): break
            info = address_info[full_address.index(address)]
            details[info] = address.strip()

        return details


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
    start = time.perf_counter()

    data_list = []
    logging.basicConfig(level=logging.INFO, filemode='w', format='%(asctime)s-%(levelname)s- %(message)s', filename='nonprofitlist.log')

    scraper = Scraper()
    logging.info('scraper initialized successfully...')

    links = scraper.get_links()
    logging.info(f'{len(links)} links found to be scraped')

    for church_link in links:
        scrape_church(church_link)

    logging.info('all threads finished scraping now exporting data')
    scraper.export_data('nonprofitlist', data_list)
    logging.info(f'{len(data_list)} lines exported')

    end = time.perf_counter()

    logging.info(f'finished in {round((end - start)//60, 2)} minutes')
