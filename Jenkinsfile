pipeline {
    agent any

    environment {
        DOCKER_IMAGE = 'abhishek4946/cms-project'
        DOCKER_CREDENTIALS_ID = 'dockerhub-credentials'
        GIT_SSL_NO_VERIFY='true'
    }

    stages {
        stage('Clone Repository') {
            steps {
                git branch: 'main', url: 'https://github.com/GantaAbhi/cms-project.git'
            }
        }

    stage('Build Docker Image') {
        steps {
            script {
                docker.build(DOCKER_IMAGE, 'app')
                }
            }
        }


        stage('Login to DockerHub') {
            steps {
                withCredentials([usernamePassword(credentialsId: DOCKER_CREDENTIALS_ID, usernameVariable: 'USERNAME', passwordVariable: 'PASSWORD')]) {
                    bat "echo %PASSWORD% | docker login -u %USERNAME% --password-stdin"
                }
            }
        }

        stage('Push Docker Image') {
            steps {
                script {
                    docker.image(DOCKER_IMAGE).push("latest")
                }
            }
        }

        stage('Deploy Container') {
            steps {
                script {
                    bat '''
                        docker ps -q --filter "name=cms-app" | findstr . && docker stop cms-app || echo "No running container"
                        docker ps -a -q --filter "name=cms-app" | findstr . && docker rm cms-app || echo "No container to remove"
                        docker run -d --name cms-app -p 5050:5000 %DOCKER_IMAGE%:latest
                    '''
                }
            }
        }
    }

    post {
        always {
            echo 'Cleaning up...'
        }
        success {
            echo '✅ CMS Project Deployed Successfully!'
        }
        failure {
            echo '❌ Deployment Failed'
        }
    }
}
