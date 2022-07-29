OPENSEARCH_RELEASE_NAME="demo"

helm-dependency-build:
	cd $(OPENSEARCH_DIR) && helm dependency build 
	cd $(OPENSEARCH_DASHBORD_DIR) && helm dependency build 

generate-opensearch-cluster-manifest:
	@cd $(OPENSEARCH_DIR) && helm template --release-name ${OPENSEARCH_RELEASE_NAME} -f values.yaml . > $(BASE_DIR)/opensearch.yaml

generate-opensearch-dashboard-manifest:
	@cd $(OPENSEARCH_DASHBORD_DIR) && helm template --release-name ${OPENSEARCH_RELEASE_NAME} -f values.yaml . > $(BASE_DIR)/opensearch-dashboard.yaml

generate-opensearch-manifest-%: generate-opensearch-cluster-manifest generate-opensearch-dashboard-manifest
	@cd $(ENVS_DIR)/$* && kustomize build

apply-opensearch-%:
	@make generate-opensearch-manifest-$* | kubectl apply -f -

clean-opensearch-%:
	@make generate-opensearch-manifest-$* | kubectl delete -f -