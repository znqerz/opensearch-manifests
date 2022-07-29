COMMON_SELF_DIR := $(dir $(lastword $(MAKEFILE_LIST)))

ifeq ($(origin ROOT_DIR),undefined)
ROOT_DIR := $(abspath $(shell cd $(COMMON_SELF_DIR)/../.. && pwd -P))
endif

OPENSEARCH_DIR=$(ROOT_DIR)/src/helm-opensearch
OPENSEARCH_DASHBORD_DIR=$(ROOT_DIR)/src/helm-opensearch-dashboard

BASE_DIR=$(ROOT_DIR)/base
ENVS_DIR=$(ROOT_DIR)/envs