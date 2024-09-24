pipeline {
  agent {
    kubernetes {
      yaml '''
        apiVersion: v1
        kind: Pod
        spec:
          hostAliases:
            - ip: 10.195.34.20
              hostnames:
                - harbor.alie.javeriana.edu.co
          containers:
          - name: docker
            image: docker.io/juancsucoder/docker_dind:latest
            args: ["--insecure-registry=zot.zot.svc.cluster.local:5000"]
            ports:
              - name: dind-con-port
                containerPort: 2376
                hostPort: 2376
                protocol: TCP
            volumeMounts:
              - name: dind-storage
                mountPath: /var/lib/docker
            env:
              - name: DOCKER_HOST
                value: "tcp://localhost:2376"
              - name: DOCKER_TLS_CERTDIR
                value: '/certs'
              - name: DOCKER_CERT_PATH
                value: '/certs/client'
              - name: DOCKER_TLS_VERIFY
                value: "1"
            tty: true
            securityContext:
              privileged: true
          volumes:
          - name: dind-storage
            persistentVolumeClaim:
              claimName: dind-storage
        '''
    }
  }
  stages {
    stage('Build-Docker-Image') {
      steps {
        container('docker') {
          sh 'docker compose build'
        }
      }
    }
    stage('Testing') {
      steps {
        container('docker') {
          sh 'cat /etc/hosts'
        }
      }
    }
    stage('Push-Images-Docker-to-Harbor') {
      steps {
        container('docker') {
          sh 'docker login -u "robot\\\$bot" -p RULNG0xjYyg8YFnkqkxkZKKcdjpbsAzY harbor.alie.javeriana.edu.co && docker compose push'
        }
      }
    }
  }
}
