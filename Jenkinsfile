pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Setup') {
            steps {
                script {
                    bat 'python -m venv venv'
                    bat 'venv\\Scripts\\activate && pip install -r requirements.txt'
                    bat 'venv\\Scripts\\activate && pip show pytest pytest-cov' // Vérifier les paquets installés
                }
            }
        }

        stage('Run Tests') {
            steps {
                script {
                    bat 'venv\\Scripts\\activate && pytest --cov=. --junitxml=report.xml || exit 1'
                }
            }
        }

        stage('Publish Test Results') {
            steps {
                junit '**/report.xml'
            }
        }
    }

    post {
        always {
            cleanWs()
        }
    }
}
