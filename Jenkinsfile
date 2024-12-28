pipeline {
    agent any

    environment {
        // Set a virtual environment directory
        VENV = '.venv'
        // Target deployment directory (simulated)
        DEPLOY_DIR = '/tmp/finalexamflaskapp'
    }

    stages {
        stage('Clone Repository') {
            steps {
                echo 'Cloning the repository...'
                git branch: 'main', url: 'https://github.com/hurjaffery/finalexamflaskapp.git'
            }
        }

        stage('Install Dependencies') {
            steps {
                echo 'Installing dependencies...'
                sh '''
                python3 -m venv ${VENV}
                source ${VENV}/bin/activate
                pip install --upgrade pip
                pip install -r requirements.txt
                '''
            }
        }

        stage('Run Unit Tests') {
            steps {
                echo 'Running unit tests...'
                sh '''
                source ${VENV}/bin/activate
                pytest --junitxml=report.xml
                '''
            }
        }

        stage('Build Application') {
            steps {
                echo 'Building the application...'
                sh '''
                source ${VENV}/bin/activate
                python setup.py build || echo "No build step defined, skipping..."
                '''
            }
        }

        stage('Deploy Application') {
            steps {
                echo 'Deploying the application...'
                sh '''
                mkdir -p ${DEPLOY_DIR}
                cp -r * ${DEPLOY_DIR}
                echo "Application deployed to ${DEPLOY_DIR}"
                '''
            }
        }
    }

    post {
        always {
            echo 'Pipeline execution completed.'
        }
        success {
            echo 'Pipeline executed successfully!'
        }
        failure {
            echo 'Pipeline failed. Please check the logs.'
        }
    }
}
