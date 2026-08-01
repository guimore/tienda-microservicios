pipeline {
    agent any

    environment {
        DOCKER_HUB_USER = 'guidomora'
        DOCKER_CREDENTIALS_ID = 'docker-hub-credentials'
    }

    stages {
        stage('Checkout') {
            steps {
                git branch: 'main', url: 'https://github.com/guidomora/tienda-microservicios.git'
            }
        }

        stage('Build Docker Images') {
            steps {
                script {
                    echo 'Construyendo imagen del Backend...'
                    sh "docker build -t ${DOCKER_HUB_USER}/tienda-backend:${BUILD_NUMBER} -t ${DOCKER_HUB_USER}/tienda-backend:latest ./backend-api"

                    echo 'Construyendo imagen del Frontend...'
                    sh "docker build -t ${DOCKER_HUB_USER}/tienda-frontend:${BUILD_NUMBER} -t ${DOCKER_HUB_USER}/tienda-frontend:latest ./frontend"
                }
            }
        }

        stage('Push Images to Docker Hub') {
            steps {
                script {
                    withCredentials([usernamePassword(credentialsId: "${DOCKER_CREDENTIALS_ID}", usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                        sh "echo $DOCKER_PASS | docker login -u $DOCKER_USER --password-stdin"
                        
                        sh "docker push ${DOCKER_HUB_USER}/tienda-backend:${BUILD_NUMBER}"
                        sh "docker push ${DOCKER_HUB_USER}/tienda-backend:latest"
                        
                        sh "docker push ${DOCKER_HUB_USER}/tienda-frontend:${BUILD_NUMBER}"
                        sh "docker push ${DOCKER_HUB_USER}/tienda-frontend:latest"
                    }
                }
            }
        }

        stage('Deploy to Kubernetes') {
            steps {
                script {
                    echo 'Aplicando manifiestos en Kubernetes...'
                    sh 'kubectl apply -f k8s/'
                    
                    sh 'kubectl rollout restart deployment/backend-deployment'
                    sh 'kubectl rollout restart deployment/frontend-deployment'
                }
            }
        }
    }

    post {
        always {
            sh 'docker logout || true'
        }
        success {
            echo '¡Despliegue exitoso en Kubernetes!'
        }
        failure {
            echo 'Error en el pipeline de CI/CD.'
        }
    }
}