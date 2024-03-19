import re
import json
import psutil
import logging

from seleniumbase import Driver
from parsel import Selector
from selector import select as se

formate_text = lambda text: re.sub(r"\n{2,}", '\n', ' '.join(text.split()))  # removing extra space or \n


def kill_process_by_name(process_name):
    """ Kills a process by its name """
    for process in psutil.process_iter():
        try:
            if process_name in process.name().lower():
                process.terminate()
                process.wait(timeout=5)
                if process.is_running():
                    process.kill()
        except psutil.AccessDenied:
            raise Exception("Couldn't Stop Chrome - please try to close it by yourself and restart this script")


def export_data(name: str, data: list[dict]) -> None:
    """ save scraped data as json """
    with open(f'{name}.json', 'w', encoding='utf-8') as export_file:
        export_file.write(json.dumps(data))


def request_clutch():
    """ request the website and get all the found profiles """
    profiles = []

    driver.open("https://www.clutch.co/logistics/manufacturing-companies/texas#")
    scrape_profiles = lambda page_source: ['https://www.clutch.co' + url for url in Selector(text=page_source, type="html").css('h3.company_info > a ::attr(href)').getall() or '' if '/profile/' in url]

    last_page = Selector(text=driver.page_source, type="html").css(se['last_page_number'])[-1].get()
    for page in range(int(last_page) + 1):
        driver.open(f"https://www.clutch.co/logistics/manufacturing-companies/texas?page={page}")
        profiles += scrape_profiles(driver.page_source)

    return profiles


def scrape_profile(link: str) -> dict[str, str]:
    driver.open(link)
    profile = Selector(text=driver.page_source, type="html")
    return {
            'name': formate_text(profile.css(se['name']).extract_first() or ''),
            'locations': [
                {
                    'address': formate_text(location.css(se["address"]).extract_first() or ''),
                    'state': location.css(se['state']).extract_first(),
                    'country': location.css(se['country']).extract_first(),
                    'zip_code': location.css(se['zip_code']).extract_first(),
                    'phone': re.sub('[(-.+)]', '', formate_text(location.css(se['phone']).extract_first() or '')).replace(' ', ''),
                } for location in profile.css(se['locations'])
            ],
            'website': profile.css(se['website']).get(),
            'linkedin': profile.css(se['linkedin']).get() or '',
            }


if __name__ == "__main__":
    kill_process_by_name('chrome')
    logging.basicConfig(level=logging.INFO, filename='clutch.log', filemode='w',
                        format='%(asctime)s - %(levelname)s - %(message)s')
    driver = Driver(
        uc=True,
        headless2=True,
        undetectable=True,
        user_data_dir='profile_1',
        dark_mode=True,
        do_not_track=True,
        ad_block_on=True,
        uc_subprocess=True,
        no_sandbox=True,
    )
    logging.info('Chrome Initialised Successfully')

    all_profiles = []
    found_profiles = request_clutch()

    logging.info(f'scraping {len(found_profiles)} profiles of companies')
    for clutch_profile in found_profiles:
        scraped_profile = scrape_profile(clutch_profile)
        print(scraped_profile)
        all_profiles.append(scraped_profile)

    logging.info(f'exporting {len(all_profiles)} rows of data')
    export_data('profiles', all_profiles)

    driver.quit()
    logging.info('Chrome Closed Successfully')
