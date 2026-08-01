pipeline {
    agent any

    environment {
        DOCKER_HUB_USER = 'guimore'
        DOCKER_CREDENTIALS_ID = 'docker-hub-credentials'
        KALI_IP = '192.168.56.104'
        SSH_CRED_ID = 'kali-ssh-key'
    }

    stages {
        stage('Checkout') {
            steps {
                git branch: 'main', url: 'https://github.com/guimore/tienda-microservicios.git'
            }
        }

        stage('Build Docker Images') {
            steps {
                sshagent([SSH_CRED_ID]) {
                    bat "ssh -o StrictHostKeyChecking=no aguila@%KALI_IP% \"cd ~/tienda-microservicios && git pull origin main && docker build -t %DOCKER_HUB_USER%/tienda-backend:%BUILD_NUMBER% -t %DOCKER_HUB_USER%/tienda-backend:latest ./backend-api\""
                    bat "ssh -o StrictHostKeyChecking=no aguila@%KALI_IP% \"cd ~/tienda-microservicios && docker build -t %DOCKER_HUB_USER%/tienda-frontend:%BUILD_NUMBER% -t %DOCKER_HUB_USER%/tienda-frontend:latest ./frontend\""
                }
            }
        }

        stage('Push Images to Docker Hub') {
            steps {
                sshagent([SSH_CRED_ID]) {
                    withCredentials([usernamePassword(credentialsId: "${DOCKER_CREDENTIALS_ID}", usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                        bat "ssh -o StrictHostKeyChecking=no aguila@%KALI_IP% \"echo %DOCKER_PASS% | docker login -u %DOCKER_USER% --password-stdin\""
                        bat "ssh -o StrictHostKeyChecking=no aguila@%KALI_IP% \"docker push %DOCKER_HUB_USER%/tienda-backend:%BUILD_NUMBER% && docker push %DOCKER_HUB_USER%/tienda-backend:latest\""
                        bat "ssh -o StrictHostKeyChecking=no aguila@%KALI_IP% \"docker push %DOCKER_HUB_USER%/tienda-frontend:%BUILD_NUMBER% && docker push %DOCKER_HUB_USER%/tienda-frontend:latest\""
                    }
                }
            }
        }

        stage('Deploy to Kubernetes') {
            steps {
                sshagent([SSH_CRED_ID]) {
                    bat "ssh -o StrictHostKeyChecking=no aguila@%KALI_IP% \"cd ~/tienda-microservicios && kubectl apply -f k8s/\""
                    bat "ssh -o StrictHostKeyChecking=no aguila@%KALI_IP% \"kubectl rollout restart deployment/backend-deployment\""
                    bat "ssh -o StrictHostKeyChecking=no aguila@%KALI_IP% \"kubectl rollout restart deployment/frontend-deployment\""
                }
            }
        }
    }
}