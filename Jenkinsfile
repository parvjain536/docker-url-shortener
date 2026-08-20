pipeline {
    agent any

    environment {
        DOCKER_HUB_USER = 'parvjn'
        IMAGE_NAME      = 'docker-url-shortener'
        DOCKER_CREDS    = credentials('docker-hub-credentials')
        DOCKER_BIN      = '\"C:\\Users\\parvj\\AppData\\Local\\Programs\\DockerDesktop\\resources\\bin\\docker.exe\"'
    }

    stages {
        stage('Checkout Code') {
            steps {
                echo 'Checking out source code from Git repository...'
                checkout scm
            }
        }

        stage('Code Quality Lint') {
            steps {
                echo 'Validating Python syntax natively...'
                bat 'python -m py_compile main.py'
            }
        }

        stage('Build Docker Image') {
            steps {
                echo "Building Docker container image for build #${env.BUILD_NUMBER}..."
                bat "%DOCKER_BIN% build -t %DOCKER_HUB_USER%/%IMAGE_NAME%:jenkins-%BUILD_NUMBER% -t %DOCKER_HUB_USER%/%IMAGE_NAME%:latest ."
            }
        }

        stage('Push to Registry') {
            steps {
                echo 'Authenticating with Docker Hub and pushing image...'
                bat "%DOCKER_BIN% login -u %DOCKER_CREDS_USR% -p %DOCKER_CREDS_PSW%"
                bat "%DOCKER_BIN% push %DOCKER_HUB_USER%/%IMAGE_NAME%:jenkins-%BUILD_NUMBER%"
                bat "%DOCKER_BIN% push %DOCKER_HUB_USER%/%IMAGE_NAME%:latest"
            }
        }
    }

    post {
        always {
            echo 'Logging out from Docker registry...'
            bat "%DOCKER_BIN% logout"
        }
        success {
            echo "Pipeline completed successfully for build #${env.BUILD_NUMBER}!"
        }
        failure {
            echo "Pipeline failed for build #${env.BUILD_NUMBER}. Check console output for debugging."
        }
    }
}