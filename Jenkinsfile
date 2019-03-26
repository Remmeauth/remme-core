pipeline {
  agent {
    label 'remme-tests-worker'
  }
  options {
    timestamps()
  }
  stages {
    stage('Test') {
      steps {
        ansiColor('xterm') {
            sh 'make test'
        }
      }
    }
  }
}
