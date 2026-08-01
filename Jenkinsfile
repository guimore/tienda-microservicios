pipeline {
    agent any

    environment {
        DOCKER_HUB_USER = 'guimore'
        DOCKER_CREDENTIALS_ID = 'docker-hub-credentials'
        // Le agregamos la ruta de Docker al PATH para esta ejecución
        PATH = "C:\\Program Files\\Docker\\Docker\\resources\\bin;${env.PATH}"
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
                    echo 'Construyendo imagen del Backend...'
                    bat "docker build -t %DOCKER_HUB_USER%/tienda-backend:%BUILD_NUMBER% -t %DOCKER_HUB_USER%/tienda-backend:latest ./backend-api"

                    echo 'Construyendo imagen del Frontend...'
                    bat "docker build -t %DOCKER_HUB_USER%/tienda-frontend:%BUILD_NUMBER% -t %DOCKER_HUB_USER%/tienda-frontend:latest ./frontend"
                }
            }
        }

        stage('Push Images to Docker Hub') {
            steps {
                script {
                    withCredentials([usernamePassword(credentialsId: "${DOCKER_CREDENTIALS_ID}", usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                        bat "echo %DOCKER_PASS% | docker login -u %DOCKER_USER% --password-stdin"
                        
                        bat "docker push %DOCKER_HUB_USER%/tienda-backend:%BUILD_NUMBER%"
                        bat "docker push %DOCKER_HUB_USER%/tienda-backend:latest"
                        
                        bat "docker push %DOCKER_HUB_USER%/tienda-frontend:%BUILD_NUMBER%"
                        bat "docker push %DOCKER_HUB_USER%/tienda-frontend:latest"
                    }
                }
            }
        }

        stage('Deploy to Kubernetes') {
            steps {
                script {
                    echo 'Aplicando manifiestos en Kubernetes...'
                    bat 'kubectl apply -f k8s/'
                    
                    bat 'kubectl rollout restart deployment/backend-deployment'
                    bat 'kubectl rollout restart deployment/frontend-deployment'
                }
            }
        }
    }

    post {
        always {
            bat 'docker logout || exit 0'
        }
        success {
            echo '¡Despliegue exitoso en Kubernetes!'
        }
        failure {
            echo 'Error en el pipeline de CI/CD.'
        }
    }
}