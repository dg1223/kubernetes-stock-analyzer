# install virtualbox or use docker driver (we'll use docker driver since docker already installed)
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube
minikube version
# start minikube using docker driver
minikube start --driver=docker