pipeline {
    agent any

    environment {
        PROD_USERNAME = 'amedikusettor'
        PROD_SERVER = '34.139.58.141'
        PROD_DIR = '/home/amedikusettor/myflix/video-catalogue'
        DOCKER_IMAGE_NAME = 'video-catalogue-deployment'
        DOCKER_CONTAINER_NAME = 'video-catalogue'
        DOCKER_CONTAINER_PORT = '5001'
        DOCKER_HOST_PORT = '5001'
    }

    stages {
        stage('Load Code to Workspace') {
            steps {
                // This step automatically checks out the code into the workspace.
                checkout scm             
            }
        }

        stage('Deploy Repo to Prod. Server') {
            steps {
                script {
                    sh 'echo Packaging files ...'
                    sh 'rsync -av . ${PROD_USERNAME}@${PROD_SERVER}:${PROD_DIR}/'
                    sh 'echo Files transferred to server. Preparing to dockerize application ...'
                    sh "ssh -o StrictHostKeyChecking=no ${PROD_USERNAME}@${PROD_SERVER} 'cd myflix/video-catalogue && ls -l'"
                    sh 'echo Repo unloaded on Prod. Server. Preparing to dockerize application ...'
                }
            }
        }


        stage('Dockerize Application') {
            steps {
                script {
                    sh "ssh -o StrictHostKeyChecking=no ${PROD_USERNAME}@${PROD_SERVER} 'cd myflix/video-catalogue && docker build -t ${DOCKER_IMAGE_NAME} .'"
                    sh "echo Docker image for videoCatalogue rebuilt. Preparing to redeploy container to web..."
                }
            }
        }

        stage('Redeploy Container to Web') {
            steps {
                script {
                    sh "ssh -o StrictHostKeyChecking=no ${PROD_USERNAME}@${PROD_SERVER} 'cd myflix/video-catalogue && docker ps -q --filter name=${DOCKER_CONTAINER_NAME} | xargs -r docker stop'"
                    sh "ssh -o StrictHostKeyChecking=no ${PROD_USERNAME}@${PROD_SERVER} 'cd myflix/video-catalogue && docker ps -q --filter name=${DOCKER_CONTAINER_NAME} | xargs -r docker rm'"

                    sh "echo Container stopped and removed. Preparing to redeploy new version"
                    sh "ssh -o StrictHostKeyChecking=no ${PROD_USERNAME}@${PROD_SERVER} 'cd myflix/video-catalogue && docker run -d -p ${DOCKER_HOST_PORT}:${DOCKER_CONTAINER_PORT} --name ${DOCKER_CONTAINER_NAME} ${DOCKER_IMAGE_NAME}'"
                    sh "echo videoCatalogue Microservice Deployed!"
                }
            }
        }
    }
}
