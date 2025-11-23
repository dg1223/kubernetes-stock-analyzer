# install kubectl (stable)
curl -fsSL https://dl.k8s.io/release/stable.txt -o /tmp/k8s-stable.txt
K8S_VER=$(cat /tmp/k8s-stable.txt)
curl -LO "https://dl.k8s.io/release/${K8S_VER}/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl
kubectl version --client