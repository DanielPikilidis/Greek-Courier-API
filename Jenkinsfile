pipeline {
    agent none
    environment {
        DOCKERHUB_CREDS = credentials('dockerhub-creds')
    }
    stages {
        stage('Checkout') {
            agent {
                kubernetes {
                    yamlFile 'jenkins/git.yaml'
                    defaultContainer 'git'
                }
            }
            steps {
                dir('/workspace') {
                    git branch:'add-jenkins', url:'https://github.com/DanielPikilidis/Greek-Courier-API.git'
                }
            }
        }
        stage('Test') {
            parallel {
                stage('Test ACS') {
                    agent {
                        kubernetes {
                            yamlFile 'jenkins/python.yaml'
                            defaultContainer 'python'
                        }
                    }
                    steps {
                        sh 'ls -al; cd /workspace/src/acs; ./test.sh;'
                    }
                }
            }
        }
        stage('Prepare Kaniko') {
            agent {
                kubernetes {
                    yamlFile 'jenkins/kaniko.yaml'
                    defaultContainer 'kaniko'
                }
            }
            steps {
                sh '''
                    echo '{"auths":{"https://index.docker.io/v1/":{"auth":"'"$(echo -n $DOCKERHUB_CREDS_USR:$DOCKERHUB_CREDS_PSW | base64)"'"}}}' \
                        > /kaniko/.docker/config.json
                '''
            }
        }
        stage('Build') {
            parallel {
                stage ("Build ACS") {
                    agent {
                        kubernetes {
                            yamlFile 'jenkins/kaniko.yaml'
                            defaultContainer 'kaniko'
                        }
                    }
                    steps {
                        sh '''
                            ls -al;
                            /kaniko/executor \
                                --context /workspace/src/acs \
                                --dockerfile /workspace/src/acs/Dockerfile \
                                --destination docker.io/dpikilidis/acs-tracker:test
                        '''
                    }
                }
            }
        }
    }
}
