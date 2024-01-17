pipeline {
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
  - name: deploy-container
    image: dtzar/helm-kubectl
    command:
    - sleep
    args:
    - infinity
'''
        }
    }
    environment {
        DOCKERHUB_CREDS = credentials('dockerhub-creds')
        KUBECONFIG = credentials('kube-config')

        ACS_COURIER_IMAGE = 'dpikilidis/acs-tracker'
        ACS_COURIER_IMAGE_TAG = 'test'
        COURIERCENTER_COURIER_IMAGE = 'dpikilidis/couriercenter-tracker'
        COURIERCENTER_COURIER_IMAGE_TAG = 'test'
        EASYMAIL_COURIER_IMAGE = 'dpikilidis/easymail-tracker'
        EASTMAIL_COURIER_IMAGE_TAG = 'test'
        ELTA_COURIER_IMAGE = 'dpikilidis/elta-tracker'
        ELTA_COURIER_IMAGE_TAG = 'test'
        GENIKI_COURIER_IMAGE = 'dpikilidis/geniki-tracker'
        GENIKI_COURIER_IMAGE_TAG = 'test'
        SKROUTZ_COURIER_IMAGE = 'dpikilidis/skroutz-tracker'
        SKROUTZ_COURIER_IMAGE_TAG = 'test'
        SPEEDEX_COURIER_IMAGE = 'dpikilidis/speedex-tracker'
        SPEEDEX_COURIER_IMAGE_TAG = 'test'
        MAIN_API_IMAGE = 'dpikilidis/main-api'
        MAIN_API_IMAGE_TAG = 'test'
        PROXY_MANAGER_IMAGE = 'dpikilidis/proxy-manager'
        PROXY_MANAGER_IMAGE_TAG = 'test'

        DEPLOYMENT_NAMESPACE = 'courier-api-prod'
    }
    stages {
        stage('Checkout') {
            steps {
                container('git') {
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
        }
        stage('Test') {
            parallel {
                stage('Test ACS') {
                    when {
                        changeset 'src/acs/**'
                    }
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

                    when {
                        changeset 'src/couriercenter/**'
                    }
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
                    when {
                        changeset 'src/easymail/**'
                    }
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
                    when {
                        changeset 'src/elta/**'
                    }
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
                    when {
                        changeset 'src/geniki/**'
                    }
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
                    when {
                        changeset 'src/skroutz/**'
                    }
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
                    when {
                        changeset 'src/speedex/**'
                    }
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
                    when {
                        changeset 'src/main-api/**'
                    }
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
                    when {
                        changeset 'src/proxy-manager/**'
                    }
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
                    when {
                        changeset 'src/acs/**'
                    }
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
                                --destination $ACS_COURIER_IMAGE:$ACS_COURIER_IMAGE_TAG
                        '''
                    }
                }
                stage ("Build CourierCenter") {
                    when {
                        changeset 'src/couriercenter/**'
                    }
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
                                --destination $COURIERCENTER_COURIER_IMAGE:$COURIERCENTER_COURIER_IMAGE_TAG
                        '''
                    }
                }
                stage ("Build EasyMail") {
                    when {
                        changeset 'src/easymail/**'
                    }
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
                                --destination $EASYMAIL_COURIER_IMAGE:$EASYMAIL_COURIER_IMAGE_TAG
                        '''
                    }
                }
                stage ("Build ELTA") {
                    when {
                        changeset 'src/elta/**'
                    }
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
                                --destination $ELTA_COURIER_IMAGE:$ELTA_COURIER_IMAGE_TAG
                        '''
                    }
                }
                stage ("Build Geniki") {
                    when {
                        changeset 'src/geniki/**'
                    }
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
                                --destination $GENIKI_COURIER_IMAGE:$GENIKI_COURIER_IMAGE_TAG
                        '''
                    }
                }
                stage ("Build Skroutz") {
                    when {
                        changeset 'src/skroutz/**'
                    }
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
                                --destination $SKROUTZ_COURIER_IMAGE:$SKROUTZ_COURIER_IMAGE_TAG
                        '''
                    }
                }
                stage ("Build Speedex") {
                    when {
                        changeset 'src/speedex/**'
                    }
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
                                --destination $SPEEDEX_COURIER_IMAGE:$SPEEDEX_COURIER_IMAGE_TAG
                        '''
                    }
                }
            }
        }
        stage('Deploy') {
            parallel {
                stage('Deploy Main API') {
                    when {
                        changeset 'src/main-api/**'
                    }
                    steps {
                        container('deploy-container') {
                            sh '''
                                mkdir -p ~/.kube
                                echo "$KUBECONFIG" > ~/.kube/config
                                cat helm/charts/acs/values.yaml
                                sed -i 's/enabled: false/enabled: true/g' helm/charts/acs/values.yaml
                                sed -i 's/repository: .*/repository: '"$MAIN_API_IMAGE"'/g' helm/charts/acs/values.yaml
                                sed -i 's/tag: .*/tag: '"$MAIN_API_IMAGE_TAG"'/g' helm/charts/acs/values.yaml


                            '''
                        }
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