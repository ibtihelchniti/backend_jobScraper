from scrapers.free_work_en import FreeWorkEn
from scrapers.free_work_fr import FreeWorkFr 
from scrapers.choose_your_boss import ChooseYourBoss
from utils.webdriver import init_webdriver
from datetime import datetime
from app import get_site_url

def main():
    driver = init_webdriver()

    # Récupérez les URL des sites depuis la base de données
    site_url_en = get_site_url(1)
    site_url_fr = get_site_url(2)
    site_url_ch = get_site_url(3)

    # Scraping du site "free work en"
    if site_url_en:
        scraper_en = FreeWorkEn(driver, site_url_en)
        scraper_en.scrape_jobs()

    # Scraping du site "free work fr"
    if site_url_fr:
        scraper_fr = FreeWorkFr(driver, site_url_fr)
        scraper_fr.scrape_jobs()

    # Scraping du site "choose your boss"
    if site_url_ch:
        scraper_ch = ChooseYourBoss(driver, site_url_ch)
        scraper_ch.scrape_jobs()

if __name__ == "__main__":
    main()
