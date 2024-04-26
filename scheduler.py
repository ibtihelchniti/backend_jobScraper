from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime

def start_scraping():
    from main import main  # Importation du main ici pour éviter la circularité

    now = datetime.now()
    print("Lancement du scraping à l'heure :", now)
    main()

# Initialisation du scheduler
scheduler = BackgroundScheduler(daemon=True)

# Ajoutez la tâche pour lancer le scraping chaque minuit
scheduler.add_job(start_scraping, 'cron', hour=0, minute=0)

# Démarrez le scheduler
scheduler.start()
