# run this in current shell when you want to build images for minikube
eval $(minikube -p minikube docker-env)
# to revert: eval $(minikube docker-env -u)