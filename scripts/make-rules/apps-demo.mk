demo-docker-build: # build demo docker images
	cd apps-demo/flask-example && docker build -t flask-example-demo:v1 .
	cd apps-demo/flask-example2 && docker build -t flask-example-demo:v2 .
	cd apps-demo/fake-request && docker build -t fake-request-example-demo:v1 .

demo-docker-push: demo-docker-build # trigger demo docker image build and load to KinD
	kind load docker-image flask-example-demo:v1 --name local-devops-envs
	kind load docker-image fake-request-example-demo:v1 --name local-devops-envs

demo-jaeger-agent-deploy:
	cd apps-demo/flask-example && kustomize edit set image demo=flask-example-demo:jaeger-agent-v1 && kustomize build | kubectl apply -f -

demo-otlp-agent-deploy:
	docker tag flask-example-demo:v1 flask-example-demo:otlp-agent-v1
	docker tag flask-example-demo:v2 flask-example-demo:otlp-agent-v2
	kind load docker-image flask-example-demo:otlp-agent-v1 --name local-devops-envs
	kind load docker-image flask-example-demo:otlp-agent-v2 --name local-devops-envs
	cd apps-demo/flask-example/deploy && kustomize edit set image demo=flask-example-demo:otlp-agent-v1 && kustomize build | kubectl apply -f -
	cd apps-demo/flask-example2/deploy && kustomize edit set image demo=flask-example-demo:otlp-agent-v2 && kustomize build | kubectl apply -f -

demo-deploy: # apply demo to local KinD
	cd apps-demo/flask-example/deploy && kustomize edit set image demo=flask-example-demo:v1  && kustomize build | kubectl apply -f -
	cd apps-demo/fake-request &&  kustomize build | kubectl apply -f -
	cd apps-demo/metric-monitor &&  kustomize build | kubectl apply -f -

demo-clean: # delete demo from KinD
	cd apps-demo/flask-example/deploy && kustomize build | kubectl delete -f -
	cd apps-demo/fake-request &&  kustomize build | kubectl delete -f -
	cd apps-demo/metric-monitor &&  kustomize build | kubectl delete -f -