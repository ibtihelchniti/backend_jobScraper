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
                bat 'python -m venv %VIRTUAL_ENV%'
                bat 'dir %VIRTUAL_ENV%'  // Vérifiez que le répertoire venv a été créé
                bat '%VIRTUAL_ENV%\\Scripts\\activate && pip install -r requirements.txt'
                bat 'pip list'  // Vérifiez que les dépendances ont été installées
            }
        }

        stage('Run Tests') {  // Troisième étape: Exécuter les tests.
            steps {
                bat """
                %VIRTUAL_ENV%\\Scripts\\activate
                pytest --cov=.
                """
            }
            post {
                always {
                    junit '**/test-results.xml'
                    archiveArtifacts artifacts: '**/coverage.xml', allowEmptyArchive: true
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
