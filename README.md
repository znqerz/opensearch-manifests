
# Opensearch-manifests

Use GitOps way to manage opensearch deploy manifests, also include tracing demo apps to try monitoring stack.

Opensearch & Opensearch Dashboards manifests are dependent on official charts, which you can find here.
[The official chart](https://opensearch-project.github.io/helm-charts/)

## What did in this manifests

At begining, I am trying to setup opensearch cluster follow production environment setup guide to start up the cluster in Kubernetes, but there is no official documents on Kubernetes `How` and `What` to do.

After few hours invested on the solution I chose the solution in the current manifests, here are short descriptions:

* To use customized and unified service account for both opensearch & opensearch-dashboard.
* To manage certs via `cert-manager` with self-signed certificate.
* To use `Kustomize` to struct deploy manifests for different environments.
* To use `Makefile` help manage generate logic.

## How to use

Run Make

```bash
# View all make commands
make help

# Generate opensearch whole staic manifests by environment.
make generate-opensearch-manifest-<ENVS>

# Apply manifests with kubectl apply
make apply-opensearch-<ENVS>

# Clean manifests with kubectl apply
make clean-opensearch-<ENVS>
```

## Production configuration suggestion

### Define clusters roles: Master, Data, Coordinating

Here are configurations

* Master Node configuration:

```yaml
nodeGroup: "master"
roles:
    - master
replicas: 1
rbac:
    serviceAccountName: "opensearch-sa"
persistence:
    size: 20Gi # set the size by yourself

extraEnvs:
- name: DISABLE_INSTALL_DEMO_CONFIG
    value: "true"
```

* Data Node Configuration:

```yaml
nodeGroup: "data"
roles:
    - ingest
    - data
replicas: 1
rbac:
    serviceAccountName: "opensearch-sa"
persistence:
    size: 50Gi
extraVolumes:
- name: opensearch-tls-key-pair
    secret:
    secretName: opensearch-tls-key-pair

extraEnvs:
- name: DISABLE_INSTALL_DEMO_CONFIG
    value: "true"

secretMounts: 
- name: opensearch-certs
    secretName: opensearch-tls-key-pair
    path: /usr/share/opensearch/config/certs
```

* Coordinating Node Configuration:

```yaml
nodeGroup: "client"
roles: []
replicas: 1
rbac:
    serviceAccountName: "opensearch-sa"
persistence:
    size: 20Gi
extraEnvs:
- name: DISABLE_INSTALL_DEMO_CONFIG
    value: "true"
secretMounts: 
- name: opensearch-certs
    secretName: opensearch-tls-key-pair
    path: /usr/share/opensearch/config/certs
```

* opensearch.yaml configuration

```yaml
config:
    opensearch.yml: |
        plugins:
            security:
            nodes_dn:
                - CN=opensearch-cluster-master.opensearch-system.svc.cluster.local
            ssl:
                transport:
                pemcert_filepath: certs/tls.crt
                pemkey_filepath: certs/tls.key
                pemtrustedcas_filepath: certs/ca.crt
                enforce_hostname_verification: false
                http:
                enabled: true
                pemcert_filepath: certs/tls.crt
                pemkey_filepath: certs/tls.key
                pemtrustedcas_filepath: certs/ca.crt
            allow_unsafe_democertificates: false
            allow_default_init_securityindex: true
            authcz:
                admin_dn:
                - CN=opensearch-cluster-master.opensearch-system.svc.cluster.local
            audit.type: internal_opensearch
            enable_snapshot_restore_privilege: true
            check_snapshot_restore_write_privileges: true
            restapi:
                roles_enabled: ["all_access", "security_rest_api_access"]
            system_indices:
                enabled: true
                indices:
                [
                    ".opendistro-alerting-config",
                    ".opendistro-alerting-alert*",
                    ".opendistro-anomaly-results*",
                    ".opendistro-anomaly-detector*",
                    ".opendistro-anomaly-checkpoints",
                    ".opendistro-anomaly-detection-state",
                    ".opendistro-reports-*",
                    ".opendistro-notifications-*",
                    ".opendistro-notebooks",
                    ".opendistro-asynchronous-search-response*",
                ]
```

## Other Docs

[GitOps Enviroments Model](https://codefresh.io/blog/how-to-model-your-gitops-environments-and-promote-releases-between-them/)

[OpenSearch performance metrics](https://docs.aws.amazon.com/zh_cn/opensearch-service/latest/developerguide/managedomains-cloudwatchmetrics.html)

[official doc via openssl commands](https://opensearch.org/docs/latest/security-plugin/configuration/generate-certificates/)

[certs via cert-manager & Let's Encrypt](https://eliatra.com/blog/opensearch-with-cert-manager-part-3-lets-encrypt/)

[good example for using cert-manager from github issue](https://github.com/opensearch-project/helm-charts/issues/115)
