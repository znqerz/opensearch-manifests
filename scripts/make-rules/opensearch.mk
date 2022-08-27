generate-opensearch-manifest-%:
	@cd $(ENVS_DIR)/$* && kustomize build --enable-helm

apply-opensearch-%:
	@make generate-opensearch-manifest-$* | kubectl apply -f -

clean-opensearch-%:
	@make generate-opensearch-manifest-$* | kubectl delete -f -