pipeline {
    agent any

    stages {
        stage('Setup') {
            steps {
                script {
                    bat 'python -m venv venv'
                    bat 'venv\\Scripts\\activate && pip install -r requirements.txt'
                }
            }
        }

        stage('Run Tests') {
            steps {
                script {
                    bat 'venv\\Scripts\\activate && pytest --cov=. --junitxml=report.xml'
                }
            }
        }

        stage('Publish Test Results') {
            steps {
                junit '**/report.xml'
            }
        }
    }
}
