import mysql.connector

def insert_job_offer_into_db(unique_id, title, company, location, job_type, salary, experience, description, logo_url):
    conn = None
    try:
        conn = mysql.connector.connect(
            user='u452481593_alawa',
            password='eLegyBaJeh',
            host='mysql',
            database='u452481593_umemy',
            port=3306

        )
        cursor = conn.cursor()

        # Vérifier si l'offre d'emploi existe déjà dans la base de données
        if get_post_id_by_unique_id(cursor, unique_id) is not None:
            print(f"L'offre d'emploi '{title}' existe déjà dans la base de données.")
            return 
        else: 
            # Insérer l'offre d'emploi dans la table lkll_posts
            query = ("""
                INSERT INTO lkll_posts (post_author, post_date, post_date_gmt, post_content, post_title, post_excerpt, 
                post_status, comment_status, ping_status, post_name, post_modified, post_modified_gmt, post_parent, 
                guid, menu_order, post_type, comment_count, to_ping, pinged, post_content_filtered) 
                VALUES (%s, NOW(), NOW(), %s, %s, '', 'publish', 'closed', 'closed', %s, NOW(), NOW(), 0, '', 0, 'job_listing', 0, '', '', '')
            """)
            data = (1, description, title, unique_id)
            cursor.execute(query, data)
            post_id = cursor.lastrowid

            # Mettre à jour les métadonnées de l'offre d'emploi
            update_postmeta(cursor, post_id, '_application', 'candidature@elzei.fr')
            update_postmeta(cursor, post_id, '_job_location', location)
            update_postmeta(cursor, post_id, '_company_name', company)
            update_postmeta(cursor, post_id, '_job_salary', salary)
            update_postmeta(cursor, post_id, '_experience_years', experience)
            update_postmeta(cursor, post_id, '_job_type', job_type)
            update_postmeta(cursor, post_id, '_company_logo', logo_url)

            job_type_id = get_term_taxonomy_id(cursor, job_type)
            if job_type_id is not None:
                add_job_to_term_relationships(cursor, post_id, job_type_id)


        # Valider la transaction
        conn.commit() 
        print(f"Offre d'emploi '{title}' ajoutée dans la base de données avec succès.")
    except mysql.connector.Error as err:
        print(f"Erreur MySQL: {err}")
        conn.rollback()
    finally:
        if conn and conn.is_connected():
            if cursor:
                cursor.close()
            conn.close()


# Fonction pour récupérer l'ID de l'offre d'emploi par son ID unique
def get_post_id_by_unique_id(cursor, unique_id):
    cursor.execute("SELECT ID FROM lkll_posts WHERE post_name = %s", (unique_id,))
    row = cursor.fetchone()
    return row[0] if row else None


# Fonction pour récupérer l'ID de la taxonomie des types d'emploi
def get_term_taxonomy_id(cursor, job_type):
    cursor.execute("SELECT term_taxonomy_id FROM lkll_term_taxonomy WHERE term_id IN (SELECT term_id FROM wp_terms WHERE name = %s)", (job_type,))
    rows = cursor.fetchall()  
    term_taxonomy_id = None
    if rows:
        term_taxonomy_id = rows[0][0] 
    return term_taxonomy_id


# Fonction pour ajouter l'offre d'emploi aux relations de termes
def add_job_to_term_relationships(cursor, post_id, term_id):
    query = """
        INSERT INTO lkll_term_relationships (object_id, term_taxonomy_id)
        VALUES (%s, %s)
    """
    cursor.execute(query, (post_id, term_id))


# Fonction pour mettre à jour les métadonnées de l'offre d'emploi   
def update_postmeta(cursor, post_id, meta_key, meta_value):
    query = ("""
        INSERT INTO lkll_postmeta (post_id, meta_key, meta_value) 
        VALUES (%s, %s, %s)
        ON DUPLICATE KEY UPDATE
        meta_value = VALUES(meta_value)
    """)
    cursor.execute(query, (post_id, meta_key, meta_value))
    

# Fonction pour insérer l'historique de scraping dans la base de données
def insert_scraping_history(scraping_date, scraping_status, site_url):
    conn = None
    try:
        conn = mysql.connector.connect(
            user='u991920173_scraping_manag',
            password='elzei@Scrap123',
            host='mysql',
            database='u991920173_elzeiscrap',
            port=3306
        )
        cursor = conn.cursor()
        
        query = "INSERT INTO scraping_history (scraping_date, scraping_status, site_url) VALUES (%s, %s, %s)"
        data = (scraping_date, scraping_status, site_url)
        cursor.execute(query, data)
        
        conn.commit()
        print("Données insérées avec succès dans la table scraping_history.")
    except mysql.connector.Error as err:
        print(f"Erreur MySQL: {err}") 
        conn.rollback()
    finally:
        if conn and conn.is_connected():
            if cursor:
                cursor.close()
            conn.close()

