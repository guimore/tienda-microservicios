pipeline {
    agent any

    environment {
        DOCKER_HUB_USER = 'gmm2'
        DOCKER_CREDENTIALS_ID = 'docker-hub-credentials'
        KALI_IP = '192.168.56.104'
        KALI_USER = 'aguila'
    }

    stages {
        stage('Checkout') {
            steps {
                git branch: 'main', url: 'https://github.com/guimore/tienda-microservicios.git'
            }
        }

        stage('Build Docker Images') {
            steps {
                script {
                    echo 'Construyendo imágenes en Kali...'
                    bat "ssh -o StrictHostKeyChecking=no -i M:\\Jenkins\\.ssh\\id_rsa %KALI_USER%@%KALI_IP% \"cd ~/tienda-microservicios && git pull origin main && docker build -t %DOCKER_HUB_USER%/tienda-backend:%BUILD_NUMBER% -t %DOCKER_HUB_USER%/tienda-backend:latest ./backend-api\""
                    bat "ssh -o StrictHostKeyChecking=no -i M:\\Jenkins\\.ssh\\id_rsa %KALI_USER%@%KALI_IP% \"cd ~/tienda-microservicios && docker build -t %DOCKER_HUB_USER%/tienda-frontend:%BUILD_NUMBER% -t %DOCKER_HUB_USER%/tienda-frontend:latest ./frontend\""
                }
            }
        }

        stage('Push Images to Docker Hub') {
            steps {
                script {
                    withCredentials([usernamePassword(credentialsId: "${DOCKER_CREDENTIALS_ID}", usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                        echo 'Pusheando imágenes a Docker Hub desde Kali...'
                        bat "ssh -o StrictHostKeyChecking=no -i M:\\Jenkins\\.ssh\\id_rsa %KALI_USER%@%KALI_IP% \"echo %DOCKER_PASS% | docker login -u %DOCKER_USER% --password-stdin\""
                        bat "ssh -o StrictHostKeyChecking=no -i M:\\Jenkins\\.ssh\\id_rsa %KALI_USER%@%KALI_IP% \"docker push %DOCKER_HUB_USER%/tienda-backend:%BUILD_NUMBER% && docker push %DOCKER_HUB_USER%/tienda-backend:latest\""
                        bat "ssh -o StrictHostKeyChecking=no -i M:\\Jenkins\\.ssh\\id_rsa %KALI_USER%@%KALI_IP% \"docker push %DOCKER_HUB_USER%/tienda-frontend:%BUILD_NUMBER% && docker push %DOCKER_HUB_USER%/tienda-frontend:latest\""
                    }
                }
            }
        }

        stage('Deploy to Kubernetes') {
            steps {
                script {
                    echo 'Aplicando manifiestos en Kubernetes...'
                    bat "ssh -o StrictHostKeyChecking=no -i M:\\Jenkins\\.ssh\\id_rsa %KALI_USER%@%KALI_IP% \"cd ~/tienda-microservicios && kubectl apply -f k8s/\""
                    bat "ssh -o StrictHostKeyChecking=no -i M:\\Jenkins\\.ssh\\id_rsa %KALI_USER%@%KALI_IP% \"kubectl rollout restart deployment/backend-deployment\""
                    bat "ssh -o StrictHostKeyChecking=no -i M:\\Jenkins\\.ssh\\id_rsa %KALI_USER%@%KALI_IP% \"kubectl rollout restart deployment/frontend-deployment\""
                }
            }
        }
    }

    post {
        always {
            bat "ssh -o StrictHostKeyChecking=no -i M:\\Jenkins\\.ssh\\id_rsa %KALI_USER%@%KALI_IP% \"docker logout || exit 0\""
        }
        success {
            echo '¡Despliegue exitoso en Kubernetes!'
        }
        failure {
            echo 'Error en el pipeline de CI/CD.'
        }
    }
}
