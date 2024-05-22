from flask import Flask, jsonify, request, send_file, redirect, url_for, session
from flask_cors import CORS
from scrapers.free_work_en import FreeWorkEn
from scrapers.free_work_fr import FreeWorkFr
from scrapers.choose_your_boss import ChooseYourBoss
from utils.webdriver import init_webdriver
from db.database import insert_scraping_history
import mysql.connector
from datetime import datetime
import os
import pandas as pd
import ldap3
from flask_httpauth import HTTPBasicAuth
from flask_ldap3_login import LDAP3LoginManager
from ldap3 import Server, Connection, SIMPLE, SYNC, ALL
from flask_login import LoginManager
from flask import session


app = Flask(__name__)
CORS(app)


# Fonction pour récupérer l'URL d'un site en fonction de son ID depuis la base de données
def get_site_url(site_id):
    try:
        conn = mysql.connector.connect(
            user='u991920173_scraping_manag',
            password='elzei@Scrap123',
            host='mysql',
            database='u991920173_elzeiscrap',
            port=3306
        )
        cursor = conn.cursor()

        # Sélectionner l'URL du site en fonction de son ID
        query = "SELECT site_url FROM scrap_config WHERE site_id = %s"
        cursor.execute(query, (site_id,))
        site_url = cursor.fetchone()

        if site_url:
            return site_url[0]  # Retourne l'URL du site
        else:
            return None
    except mysql.connector.Error as err:
        print(f"Erreur MySQL: {err}")
        return None
    finally:
        if conn and conn.is_connected():
            if cursor:
                cursor.close()
            conn.close()

# Route pour obtenir les détails d'un site en fonction de son ID
@app.route('/site-details/<int:site_id>', methods=['GET'])
def get_site_details(site_id):
    try:
        conn = mysql.connector.connect(
            user='u991920173_scraping_manag',
            password='elzei@Scrap123',
            host='mysql',
            database='u991920173_elzeiscrap',
            port=3306
        )
        cursor = conn.cursor(dictionary=True)

        # Sélectionner les détails du site en fonction de son ID
        query = "SELECT site_name, site_url FROM scrap_config WHERE site_id = %s"
        cursor.execute(query, (site_id,))
        site_details = cursor.fetchone()

        if site_details:
            return jsonify(site_details)  
        else:
            return jsonify({"error": "Site not found"}), 404
    except mysql.connector.Error as err:
        print(f"Erreur MySQL: {err}")
        return jsonify({"error": str(err)}), 500
    finally:
        if conn and conn.is_connected():
            if cursor:
                cursor.close()
            conn.close()


# Route pour scraper les offres d'emploi depuis Free Work En    
@app.route('/scrape-en', methods=['GET'])
def scrape_jobs_en():
    try:
        driver = init_webdriver()
        site_id = 1  # ID de Free Work En
        site_url = get_site_url(site_id)  # Récupérer l'URL du site en fonction de son ID
        
        if site_url:
            scraper = FreeWorkEn(driver, site_url) # Initialiser le scraper
            scraper.scrape_jobs() # Scraper les offres d'emploi
            insert_scraping_history(datetime.now(), "Success", site_url) # Insérer l'historique de scraping 
            return jsonify({"success": True, "message": "Scraping terminé avec succès."})
        else:
            print("URL du site non trouvée dans la base de données.")
            insert_scraping_history(datetime.now(), "Failed", "URL non trouvée")
            return jsonify({"success": False, "message": "URL du site non trouvée."})
    except Exception as e:
        insert_scraping_history(datetime.now(), "Failed", site_url if site_url else "URL non trouvée")
        return jsonify({"success": False, "message": str(e)})


# Route pour scraper les offres d'emploi depuis Free Work Fr
@app.route('/scrape-fr', methods=['GET'])
def scrape_jobs_fr():
    try:
        driver = init_webdriver()
        site_id = 2  # ID de Free Work Fr
        site_url = get_site_url(site_id)  # Récupérer l'URL du site en fonction de son ID

        if site_url:
            scraper = FreeWorkFr(driver, site_url)  # Initialiser le scraper
            scraper.scrape_jobs() # Scraper les offres d'emploi
            insert_scraping_history(datetime.now(), "Success", site_url) # Insérer l'historique de scraping
            return jsonify({"success": True, "message": "Scraping terminé avec succès."})
        else:
            print("URL du site non trouvée dans la base de données.")
            insert_scraping_history(datetime.now(), "Failed", "URL non trouvée")
            return jsonify({"success": False, "message": "URL du site non trouvée."})
    except Exception as e:
        insert_scraping_history(datetime.now(), "Failed", site_url if site_url else "URL non trouvée")
        return jsonify({"success": False, "message": str(e)})
    

# Route pour scraper les offres d'emploi depuis Choose Your Boss
@app.route('/scrape-ch', methods=['GET'])
def scrape_jobs_ch():
    try:
        driver = init_webdriver()
        site_id = 3  # ID de Choose Your Boss
        site_url = get_site_url(site_id)  # Récupérer l'URL du site en fonction de son ID

        if site_url:
            scraper = ChooseYourBoss(driver, site_url) # Initialiser le scraper 
            scraper.scrape_jobs() # Scraper les offres d'emploi
            insert_scraping_history(datetime.now(), "Success", site_url) # Insérer l'historique de scraping
            return jsonify({"success": True, "message": "Scraping terminé avec succès."})
        else:
            print("URL du site non trouvée dans la base de données.")
            insert_scraping_history(datetime.now(), "Failed", "URL non trouvée")
            return jsonify({"success": False, "message": "URL du site non trouvée."})
    except Exception as e:
        insert_scraping_history(datetime.now(), "Failed", site_url if site_url else "URL non trouvée")
        return jsonify({"success": False, "message": str(e)})
    
    
# Route pour récupérer l'historique de scraping
@app.route('/scraping-history', methods=['GET'])
def get_scraping_history():
    try:
        conn = mysql.connector.connect(
            user='u991920173_scraping_manag',
            password='elzei@Scrap123',
            host='mysql',
            database='u991920173_elzeiscrap',
            port=3306
        )
        cursor = conn.cursor(dictionary=True)

        scraping_history = []

        # Sélectionner les informations d'historique de scraping depuis la base de données
        query = "SELECT site_url, scraping_date, scraping_status FROM scraping_history ORDER BY scraping_date DESC"
        cursor.execute(query)
        history_data = cursor.fetchall()

        # Formatage des données récupérées
        for row in history_data:
            site_info = {
                "site_url": row['site_url'],
                "lastScrapingDate": row['scraping_date'].strftime('%Y-%m-%d %H:%M:%S'),
                "scrapingStatus": row['scraping_status']
            }
            scraping_history.append(site_info)

        return jsonify(scraping_history)
    except mysql.connector.Error as err:
        print(f"Erreur MySQL: {err}")
        return jsonify({"error": str(err)}), 500
    finally:
        if conn and conn.is_connected():
            if cursor:
                cursor.close()
            conn.close()


# Route pour exporter les données en CSV
@app.route('/export-csv', methods=['GET'])
def export_csv():
    # Récupérer l'ID du site à partir de la requête
    site_id = request.args.get('site_id')

    # Sélectionnez le scraper en fonction de l'ID du site
    if site_id == '1':  # ID du site Free Work En
        scraper = FreeWorkEn(init_webdriver())
        csv_file = f'free_work_en_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'  # Ajouter un horodatage au nom du fichier
    elif site_id == '2':  # ID du site Free Work Fr
        scraper = FreeWorkFr(init_webdriver())
        csv_file = f'free_work_fr_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'  # Ajouter un horodatage au nom du fichier
    elif site_id == '3':  # ID du site Choose Your Boss
        # Récupérer l'URL du site à partir de la fonction get_site_url
        site_url = get_site_url(site_id)
        if site_url:
            scraper = ChooseYourBoss(init_webdriver(), site_url)  # Passer l'URL du site au scraper
            csv_file = f'choose_your_boss_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'  # Ajouter un horodatage au nom du fichier
        else:
            return jsonify({"error": "URL du site non trouvée dans la base de données"}), 404
    else:
        return jsonify({"error": "Site non pris en charge"}), 400

    # Scraper les données pour le site spécifié
    data = scraper.scrape_jobs()

    if data:
        try:
            # Convertir les données en DataFrame Pandas
            df = pd.DataFrame(data)

            # Réorganiser les colonnes selon la structure souhaitée
            df = df[['unique_id', 'title', 'company', 'location', 'job_type', 'logo_url', 'salary', 'experience', 'description']]

            # Écrire les données dans un fichier CSV temporaire
            csv_file_path = os.path.join(app.root_path, '..', 'csv', csv_file)  # Chemin vers le dossier 'csv'
            df.to_csv(csv_file_path, index=False, encoding='utf-8-sig')

            insert_scraping_history(datetime.now(), "Success", site_url)

            # Renvoyer le fichier CSV en tant que pièce jointe avec un nom spécifié pour le téléchargement
            return send_file(csv_file_path, as_attachment=True)
        except Exception as e:
            return jsonify({"error": f"Erreur lors de l'exportation en CSV : {str(e)}"}), 500

    else:
        return jsonify({"error": "Aucune donnée à exporter"}), 404

  
# Route pour mettre à jour les détails du site
@app.route('/site-details/<int:site_id>', methods=['PUT'])
def update_site_details(site_id):
    try:
        # Récupérer les données JSON de la requête
        data = request.get_json()

        # Extraire le nouveau nom et l'URL du site à partir des données JSON
        new_name = data.get('name')
        new_url = data.get('url')

        # Mettre à jour le nom et l'URL du site dans la base de données en utilisant l'ID du site
        conn = mysql.connector.connect(
            user='u991920173_scraping_manag',
            password='elzei@Scrap123',
            host='mysql',
            database='u991920173_elzeiscrap',
            port=3306
        )
        cursor = conn.cursor()

        query = "UPDATE scrap_config SET site_name = %s, site_url = %s WHERE site_id = %s"
        cursor.execute(query, (new_name, new_url, site_id))
        conn.commit()

        return jsonify({"success": True, "message": "Détails du site mis à jour avec succès."})
    except mysql.connector.Error as err:
        print(f"Erreur MySQL: {err}")
        return jsonify({"error": str(err)}), 500
    finally:
        if conn and conn.is_connected():
            if cursor:
                cursor.close()
            conn.close()




# Configuration LDAP
app.config['LDAP_HOST'] = 'ldap://elzei-uat.esy.es:389'
app.config['LDAP_BASE_DN'] = 'ou=system'
app.config['LDAP_BIND_USER_DN'] = 'uid=admin,ou=system'
app.config['LDAP_BIND_USER_PASSWORD'] = 'secret'

# Initialisation de LDAP manager
ldap_manager = LDAP3LoginManager(app)
ldap_manager.init_app(app)

# Initialisation du LoginManager Flask-Login
login_manager = LoginManager(app)
login_manager.login_view = 'login'

app.secret_key = 'c2f2eca4a9d05b6747edc063f90e49c7'


# Authentification HTTP basique
basic_auth = HTTPBasicAuth()

# Fonction de vérification des identifiants
@basic_auth.verify_password
def verify_password(username, password):
    try:
        # Création des objets de serveur et de connexion LDAP
        server = Server(app.config['LDAP_HOST'], get_info=ALL)
        connection = Connection(server, user=app.config['LDAP_BIND_USER_DN'], password=app.config['LDAP_BIND_USER_PASSWORD'], authentication=SIMPLE)

        # Tentative de connexion LDAP et d'authentification
        if connection.bind():
            print("Connexion LDAP réussie")  

            # Construction du filtre LDAP pour le nom d'utilisateur
            search_filter = f'(cn={username})'
            connection.search(app.config['LDAP_BASE_DN'], search_filter, attributes=['cn', 'userPassword'])

            # Vérification de l'existence de l'entrée utilisateur
            entries = connection.response
            if entries and entries[0]['dn']:
                user_dn = entries[0]['dn']
                user_password = entries[0]['attributes']['userPassword'][0].decode('utf-8')  # Récupération du mot de passe encodé
                # Vérification du mot de passe
                if connection.rebind(user=user_dn, password=password):
                    print("Mot de passe correct") 
                    return True
                else:
                    print("Mot de passe incorrect") 
                    return False
            else:
                print("Utilisateur introuvable dans LDAP")  
                return False
        else:
            print("Échec de la connexion LDAP")  
            return False
    except Exception as e:
        print(f"Erreur LDAP: {e}")  
        return False


# Route de connexion
@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    
    print(f"Nom d'utilisateur: {username}")
    print(f"Mot de passe: {password}")
    
    # Vérification du nom d'utilisateur et du mot de passe par rapport à LDAP
    if verify_password(username, password):
        print("Authentification réussie")
        session['username'] = username  # Stocker le nom d'utilisateur dans la session Flask
        return jsonify({'message': 'Authentification réussie'}), 200
    else:
        print("Échec de l'authentification")
        return jsonify({'message': 'Nom d\'utilisateur ou mot de passe incorrect'}), 


# Route de déconnexion
@app.route('/logout', methods=['POST'])
def logout():
    # Vérifier si l'utilisateur est connecté avant de le déconnecter
    if session.get('logged_in'):
        # Supprimer uniquement la variable de session liée à la connexion
        session.pop('logged_in', None)
        return jsonify({'message': 'Déconnexion réussie'}), 200
    else:
        return jsonify({'message': 'Utilisateur non connecté'}), 401



if __name__ == '__main__':
    app.run()
    
    

