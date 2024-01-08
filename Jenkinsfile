pipeline {
    agent any
    environment {
        DOCKERHUB_CREDS = credentials('dockerhub-creds')
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
    volumeMounts:
    - name: shared-volume
      mountPath: /workspace
  volumes:
  - name: shared-volume
    emptyDir: {}
                    '''
                }
            }
            steps {
                dir('workspace') {
                    git branch:'add-jenkins', url:'https://github.com/DanielPikilidis/Greek-Courier-API.git'
                }

                script {
                    def pythonTemplateYaml = readFile('workspace/jenkins/python.yaml')
                    env.PYTHON_TEMPLATE = pythonTemplateYaml
                    def golangTemplateYaml = readFile('workspace/jenkins/golang.yaml')
                    env.GOLANG_TEMPLATE = golangTemplateYaml
                    def kanikoTemplateYaml = readFile('workspace/jenkins/kaniko.yaml')
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
                        }
                    }
                    steps {
                        sh 'ls -al; cd workspace/src/acs; ./test.sh;'
                    }
                }
            }
        }
        stage('Prepare Kaniko') {
            agent {
                kubernetes {
                    yaml env.KANIKO_TEMPLATE
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
                            yaml env.KANIKO_TEMPLATE
                        }
                    }
                    steps {
                        sh '''
                            ls -al;
                            /kaniko/executor \
                                --context workspace/src/acs \
                                --dockerfile workspace/src/acs/Dockerfile \
                                --destination docker.io/dpikilidis/acs-tracker:test
                        '''
                    }
                }
            }
        }
    }
}