pipeline {
    agent any
    environment {
        DOCKERHUB_CREDS = credentials('dockerhub-creds')

        ACS_COURIER_IMAGE = 'dpikilidis/acs-tracker:test'
        COURIERCENTER_COURIER_IMAGE = 'dpikilidis/couriercenter-tracker:test'
        EASYMAIL_COURIER_IMAGE = 'dpikilidis/easymail-tracker:test'
        ELTA_COURIER_IMAGE = 'dpikilidis/elta-tracker:test'
        GENIKI_COURIER_IMAGE = 'dpikilidis/geniki-tracker:test'
        SKROUTZ_COURIER_IMAGE = 'dpikilidis/skroutz-tracker:test'
        SPEEDEX_COURIER_IMAGE = 'dpikilidis/speedex-tracker:test'
        MAIN_API_IMAGE = 'dpikilidis/main-api:test'
        PROXY_MANAGER_IMAGE = 'dpikilidis/proxy-manager:test'
    }
    stages {
        stage('Checkout') {
            agent {
                kubernetes {
                    yaml '''
apiVersion: v1
kind: Pod
spec:
  containers:
  - name: git
    image: alpine/git
    command:
    - sleep
    args:
    - infinity
                    '''
                }
            }
            steps {
                git branch:'add-jenkins', url:'https://github.com/DanielPikilidis/Greek-Courier-API.git'

                stash includes: 'src/**/*', name: 'src'
                stash includes: 'helm/**/*', name: 'helm'

                script {
                    def pythonTemplateYaml = readFile('jenkins/python.yaml')
                    env.PYTHON_TEMPLATE = pythonTemplateYaml
                    def golangTemplateYaml = readFile('jenkins/golang.yaml')
                    env.GOLANG_TEMPLATE = golangTemplateYaml
                    def kanikoTemplateYaml = readFile('jenkins/kaniko.yaml')
                    env.KANIKO_TEMPLATE = kanikoTemplateYaml
                }
            }
        }
        stage('Test') {
            parallel {
                stage('Test ACS') {
                    agent {
                        kubernetes {
                            yaml env.PYTHON_TEMPLATE
                            defaultContainer 'python'
                        }
                    }
                    steps {
                        unstash 'src'
                        
                        sh 'cd src/acs; ./test.sh'
                    }
                }
                stage('Test CourierCenter') {
                    agent {
                        kubernetes {
                            yaml env.PYTHON_TEMPLATE
                            defaultContainer 'python'
                        }
                    }
                    steps {
                        unstash 'src'
                        
                        sh 'cd src/couriercenter; ./test.sh'
                    }
                }
                stage('Test EasyMail') {
                    agent {
                        kubernetes {
                            yaml env.PYTHON_TEMPLATE
                            defaultContainer 'python'
                        }
                    }
                    steps {
                        unstash 'src'
                        
                        sh 'cd src/easymail; ./test.sh'
                    }
                }
                stage('Test ELTA') {
                    agent {
                        kubernetes {
                            yaml env.PYTHON_TEMPLATE
                            defaultContainer 'python'
                        }
                    }
                    steps {
                        unstash 'src'
                        
                        sh 'cd src/elta; ./test.sh'
                    }
                }
                stage('Test Geniki') {
                    agent {
                        kubernetes {
                            yaml env.PYTHON_TEMPLATE
                            defaultContainer 'python'
                        }
                    }
                    steps {
                        unstash 'src'
                        
                        sh 'cd src/geniki; ./test.sh'
                    }
                }
                stage('Test Skroutz') {
                    agent {
                        kubernetes {
                            yaml env.GOLANG_TEMPLATE
                            defaultContainer 'golang'
                        }
                    }
                    steps {
                        unstash 'src'
                        
                        sh 'cd src/skroutz; ./test.sh'
                    }
                }
                stage('Test Speedex') {
                    agent {
                        kubernetes {
                            yaml env.PYTHON_TEMPLATE
                            defaultContainer 'python'
                        }
                    }
                    steps {
                        unstash 'src'
                        
                        sh 'cd src/speedex; ./test.sh'
                    }
                }
            }
        }
        stage('Build') {
            parallel {
                stage ("Build Main API") {
                    agent {
                        kubernetes {
                            yaml env.KANIKO_TEMPLATE
                            defaultContainer 'kaniko'
                        }
                    }
                    steps {
                        unstash 'src'
                        sh '''
                            echo '{"auths":{"https://index.docker.io/v1/":{"auth":"'"$(echo -n $DOCKERHUB_CREDS_USR:$DOCKERHUB_CREDS_PSW | base64)"'"}}}' > /kaniko/.docker/config.json;
                            /kaniko/executor \
                                --context src/main-api \
                                --dockerfile src/main-api/Dockerfile \
                                --destination $MAIN_API_IMAGE
                        '''
                    }
                }
                stage ("Build Proxy Manager") {
                    agent {
                        kubernetes {
                            yaml env.KANIKO_TEMPLATE
                            defaultContainer 'kaniko'
                        }
                    }
                    steps {
                        unstash 'src'
                        sh '''
                            echo '{"auths":{"https://index.docker.io/v1/":{"auth":"'"$(echo -n $DOCKERHUB_CREDS_USR:$DOCKERHUB_CREDS_PSW | base64)"'"}}}' > /kaniko/.docker/config.json;
                            /kaniko/executor \
                                --context src/proxy-manager \
                                --dockerfile src/proxy-manager/Dockerfile \
                                --destination $PROXY_MANAGER_IMAGE
                        '''
                    }
                }
                stage ("Build ACS") {
                    agent {
                        kubernetes {
                            yaml env.KANIKO_TEMPLATE
                            defaultContainer 'kaniko'
                        }
                    }
                    steps {
                        unstash 'src'
                        sh '''
                            echo '{"auths":{"https://index.docker.io/v1/":{"auth":"'"$(echo -n $DOCKERHUB_CREDS_USR:$DOCKERHUB_CREDS_PSW | base64)"'"}}}' > /kaniko/.docker/config.json;
                            /kaniko/executor \
                                --context src/acs \
                                --dockerfile src/acs/Dockerfile \
                                --destination $ACS_COURIER_IMAGE
                        '''
                    }
                }
                stage ("Build CourierCenter") {
                    agent {
                        kubernetes {
                            yaml env.KANIKO_TEMPLATE
                            defaultContainer 'kaniko'
                        }
                    }
                    steps {
                        unstash 'src'
                        sh '''
                            echo '{"auths":{"https://index.docker.io/v1/":{"auth":"'"$(echo -n $DOCKERHUB_CREDS_USR:$DOCKERHUB_CREDS_PSW | base64)"'"}}}' > /kaniko/.docker/config.json;
                            /kaniko/executor \
                                --context src/couriercenter \
                                --dockerfile src/couriercenter/Dockerfile \
                                --destination $COURIERCENTER_COURIER_IMAGE
                        '''
                    }
                }
                stage ("Build EasyMail") {
                    agent {
                        kubernetes {
                            yaml env.KANIKO_TEMPLATE
                            defaultContainer 'kaniko'
                        }
                    }
                    steps {
                        unstash 'src'
                        sh '''
                            echo '{"auths":{"https://index.docker.io/v1/":{"auth":"'"$(echo -n $DOCKERHUB_CREDS_USR:$DOCKERHUB_CREDS_PSW | base64)"'"}}}' > /kaniko/.docker/config.json;
                            /kaniko/executor \
                                --context src/easymail \
                                --dockerfile src/easymail/Dockerfile \
                                --destination $EASYMAIL_COURIER_IMAGE
                        '''
                    }
                }
                stage ("Build ELTA") {
                    agent {
                        kubernetes {
                            yaml env.KANIKO_TEMPLATE
                            defaultContainer 'kaniko'
                        }
                    }
                    steps {
                        unstash 'src'
                        sh '''
                            echo '{"auths":{"https://index.docker.io/v1/":{"auth":"'"$(echo -n $DOCKERHUB_CREDS_USR:$DOCKERHUB_CREDS_PSW | base64)"'"}}}' > /kaniko/.docker/config.json;
                            /kaniko/executor \
                                --context src/elta \
                                --dockerfile src/elta/Dockerfile \
                                --destination $ELTA_COURIER_IMAGE
                        '''
                    }
                }
                stage ("Build Geniki") {
                    agent {
                        kubernetes {
                            yaml env.KANIKO_TEMPLATE
                            defaultContainer 'kaniko'
                        }
                    }
                    steps {
                        unstash 'src'
                        sh '''
                            echo '{"auths":{"https://index.docker.io/v1/":{"auth":"'"$(echo -n $DOCKERHUB_CREDS_USR:$DOCKERHUB_CREDS_PSW | base64)"'"}}}' > /kaniko/.docker/config.json;
                            /kaniko/executor \
                                --context src/geniki \
                                --dockerfile src/geniki/Dockerfile \
                                --destination $GENIKI_COURIER_IMAGE
                        '''
                    }
                }
                stage ("Build Skroutz") {
                    agent {
                        kubernetes {
                            yaml env.KANIKO_TEMPLATE
                            defaultContainer 'kaniko'
                        }
                    }
                    steps {
                        unstash 'src'
                        sh '''
                            echo '{"auths":{"https://index.docker.io/v1/":{"auth":"'"$(echo -n $DOCKERHUB_CREDS_USR:$DOCKERHUB_CREDS_PSW | base64)"'"}}}' > /kaniko/.docker/config.json;
                            /kaniko/executor \
                                --context src/skroutz \
                                --dockerfile src/skroutz/Dockerfile \
                                --destination $SKROUTZ_COURIER_IMAGE
                        '''
                    }
                }
                stage ("Build Speedex") {
                    agent {
                        kubernetes {
                            yaml env.KANIKO_TEMPLATE
                            defaultContainer 'kaniko'
                        }
                    }
                    steps {
                        unstash 'src'
                        sh '''
                            echo '{"auths":{"https://index.docker.io/v1/":{"auth":"'"$(echo -n $DOCKERHUB_CREDS_USR:$DOCKERHUB_CREDS_PSW | base64)"'"}}}' > /kaniko/.docker/config.json;
                            /kaniko/executor \
                                --context src/speedex \
                                --dockerfile src/speedex/Dockerfile \
                                --destination $SPEEDEX_COURIER_IMAGE
                        '''
                    }
                }
            }
        }
    }
    post {
        always {
            cleanWs()
        }
    }
}