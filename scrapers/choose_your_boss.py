from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import hashlib
from .base_scraper import BaseScraper
from db.database import insert_job_offer_into_db
import mysql.connector  



# Définition de la classe qui hérite de base scraper
class ChooseYourBoss(BaseScraper):
    def __init__(self, driver, site_url):
        super().__init__(site_url) # Initialisation de la classe de base
        self.driver = driver # Initialisation du pilote Selenium
        self.scraped_data = [] # Liste pour stocker les données scrapées


    # Méthode pour récupérer l'URL du site à partir de son ID en base de données  
    def get_site_url(site_id):
        try:
            conn = mysql.connector.connect(
                user='root',
                password='Ibtihel456@Chniti',
                host='localhost',
                database='scraping_management',
                port=3306
            )
            cursor = conn.cursor()
            query = "SELECT site_url FROM scrap_config WHERE site_id = %s"
            cursor.execute(query, (site_id,))
            result = cursor.fetchone()
            if result:
                return result[0]  # Retourne l'URL du site
            else:
                return None
        except mysql.connector.Error as err:
            print(f"Erreur MySQL: {err}")
            return None
        finally:
            if conn and conn.is_connected():
                cursor.close()
                conn.close()


    # Méthode principale pour scraper les offres d'emploi
    def scrape_jobs(self):
        try:
            self.driver.get(self.url) # Accéder à l'URL du site
            while True:
                self._wait_for_job_elements() # Attendre que les éléments d'offre d'emploi soient chargés
                self._scrape_current_page() # Scraper la page actuelle
                if not self._go_to_next_page(): # Passer à la page suivante
                    print("Fin des pages d'offre d'emploi.")
                    break
        except Exception as e:
            print(f"Erreur lors du scraping : {e}")
        finally:
            self.driver.quit() # Fermer le navigateur Selenium
        
        return self.scraped_data


    
    # Méthode pour attendre que les éléments d'offre d'emploi soient chargés
    def _wait_for_job_elements(self):
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.col-md-8.col-xs-12 > div.card.offer')))

    
    # Méthode pour cliquer sur le bouton "Voir l'offre d'emploi"
    def _click_view_job_button(self, job_element):
        try:
            job_url = job_element.find_element(By.CSS_SELECTOR, '.offer__title.top a').get_attribute('href') # Récupérer l'URL de l'offre
            self.driver.execute_script(f"window.open('{job_url}','_blank');") # Ouvrir l'URL dans une nouvelle fenêtre
            self.driver.switch_to.window(self.driver.window_handles[-1]) # Passer à la nouvelle fenêtre
            time.sleep(3) # Attendre le chargement de la page 
        except Exception as e:
            print(f"Impossible d'ouvrir l'URL de l'offre d'emploi : {e}")

    
    # Méthode pour scraper les détails de l'offre sur la page actuelle
    def _scrape_current_page(self):
        while True:
            job_offers = self.driver.find_elements(By.CSS_SELECTOR, 'div.col-md-8.col-xs-12 > div.card.offer ')
            for job in job_offers:
                try:
                    self._click_view_job_button(job)  # Ouvre la page d'offre d'emploi
                    
                    WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, ' div.well > div'))) # Attendre que la page de détails de l'offre soit chargée
                    
                    # Scraper les détails de l'offre
                    job_details = self.driver.find_element(By.CSS_SELECTOR, 'div.container-fluid')
                    title = self._get_element_text(job_details, 'div.headline > h1')
                    company = self._get_element_text(job_details, 'div.headline > div > a')
                    job_type = self._get_element_text(job_details, 'div.details > ul > li:nth-child(1)')
                    salary = self._get_element_text(job_details, 'div.details > ul > li:nth-child(2)')
                    experience = self._get_element_text(job_details, 'div.details > ul > li:nth-child(3)')
                    location = self._get_element_text(job_details, 'div.details > ul > li:nth-child(4)')
                    unique_id = hashlib.md5((title + company).encode('utf-8')).hexdigest()

                    # Scraper la description de l'offre tout en conservant la mise en forme
                    job_description = self.driver.find_element(By.CSS_SELECTOR, 'div.col-xs-12.col-md-8')
                    description_elements = job_description.find_elements(By.CSS_SELECTOR, 'div.well > div')
                    description = '\n\n\n'.join([element.get_attribute('innerHTML') for element in description_elements])

                    # Scraper l'URL du logo de l'entreprise si l'élément est présent
                    logo_elements = self.driver.find_elements(By.CSS_SELECTOR, 'div.thumbnail.thumbnail-xl.thumbnail--light > img.img-responsive')
                    if logo_elements:
                        logo_url = logo_elements[0].get_attribute('src')
                    else:
                        logo_url = None

                    # Imprimer les détails de l'offre
                    print(f'Titre: {title}\nEntreprise: {company}\nLocalisation: {location}\nType: {job_type}\nLogo: {logo_url}\nSalaire: {salary}\nExpérience nécessaire: {experience}\nDescription: {description}\n{"-"*20}')

                    # Insérer les détails de l'offre dans la base de données
                    insert_job_offer_into_db(unique_id, title, company, location, job_type, salary, experience, description, logo_url)

                    self.scraped_data.append({
                        "unique_id": unique_id,
                        "title": title,
                        "company": company,
                        "location": location,
                        "job_type": job_type,
                        "salary": salary,
                        "experience": experience,
                        "description": description,
                        "logo_url": logo_url,
                    })

                except Exception as e:
                    print(f"Erreur lors du scraping de cette offre : {e}")
                    
                finally:
                    # Fermer la fenêtre actuelle et revenir à la fenêtre précédente
                    if len(self.driver.window_handles) > 1:
                        self.driver.close()
                        self.driver.switch_to.window(self.driver.window_handles[0])
                    time.sleep(3)  # Attendre que la page se recharge

            if not self._go_to_next_page():
                break

    
    # Méthode pour passer à la page suivante
    def _get_element_text(self, parent_element, css_selector, default="-"):
        try:
            return parent_element.find_element(By.CSS_SELECTOR, css_selector).text.strip()
        except:
            return default

    
    # Méthode pour récupérer le texte d'un élément
    def _go_to_next_page(self):
        try:
            next_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'ul.pagination li:last-child a[rel="next"]'))
            )
            next_button.click()
            time.sleep(3)
            return True
        except Exception as e:
            print(f"Impossible de passer à la page suivante : {e}")
            return False




    