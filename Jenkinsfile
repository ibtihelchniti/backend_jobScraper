pipeline {
    agent any  // Utilise n'importe quel agent disponible pour exécuter la pipeline.

    environment {
        VIRTUAL_ENV = 'venv'  // Définis une variable d'environnement pour l'environnement virtuel Python.
    }

    stages {
        stage('Checkout') {  // Première étape: Récupérer le code depuis GitHub.
            steps {
                git 'https://github.com/ibtihelchniti/backend_jobScraper.git'
            }
        }

        stage('Setup') {  // Deuxième étape: Configurer l'environnement.
            steps {
                bat 'python -m venv %VIRTUAL_ENV%'  // Crée un environnement virtuel.
                bat '%VIRTUAL_ENV%\\Scripts\\activate && pip install -r requirements.txt'  // Active l'environnement virtuel et installe les dépendances.
            }
        }

        stage('Run Tests') {  // Troisième étape: Exécuter les tests.
            steps {
                bat '%VIRTUAL_ENV%\\Scripts\\activate && pytest --cov=.'  // Active l'environnement virtuel et exécute les tests avec couverture de code.
            }
            post {
                always {
                    junit '**/test-results.xml'  // Analyse les résultats des tests (si pytest les exporte en XML).
                    archiveArtifacts artifacts: '**/coverage.xml', allowEmptyArchive: true  // Archive les rapports de couverture de tests.
                }
            }
        }
    }

    post {
        always {
            cleanWs()  // Nettoie l'espace de travail après chaque build.
        }
        success {
            echo 'Pipeline completed successfully!'  // Message de succès.
        }
        failure {
            echo 'Pipeline failed, please check the logs.'  // Message d'échec.
        }
    }
}
