
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

```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
configMapGenerator:
# generate a ConfigMap named my-java-server-props-<some-hash> where each file
# in the list appears as a data entry (keyed by base filename).
- name: my-java-server-props
  files:
  - application.properties
  - more.properties
# generate a ConfigMap named my-java-server-env-vars-<some-hash> where each literal
# in the list appears as a data entry (keyed by literal key).
- name: my-java-server-env-vars
  literals:    
  - JAVA_HOME=/opt/java/jdk
  - JAVA_TOOL_OPTIONS=-agentlib:hprof
# generate a ConfigMap named my-system-env-<some-hash> where each key/value pair in the
# env.txt appears as a data entry (separated by \n).
- name: my-system-env
  env: env.txt
```

```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
secretGenerator:
  # generate a tls Secret
- name: app-tls
  files:
    - secret/tls.cert
    - secret/tls.key
  type: "kubernetes.io/tls"
- name: env_file_secret
  # env is a path to a file to read lines of key=val
  # you can only specify one env file per secret.
  env: env.txt
  type: Opaque
```

```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

namespace: nginx

bases:
  - ../base-folder

resources:
  - https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/kind/deploy.yaml
  - ./namespace.yaml
```

```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

namePrefix: "demo-prefix-"
nameSuffix: "-demo-suffix"

namespace: "my-app-namespace"

commonAnnotations:
  annotationKey1: "annotationValue1"

commonLabels:
  labelKey1: "labelValue1"

images:
  - name: postgres
    newName: my-registry/my-postgres
    newTag: v1

vars:
  - name: SOME_SECRET_NAME
    objref:
      kind: Secret
      name: my-secret
      apiVersion: v1
  - name: MY_SERVICE_NAME
    objref:
      kind: Service
      name: my-service
      apiVersion: v1
    fieldref:
      fieldpath: metadata.name
  - name: ANOTHER_DEPLOYMENTS_POD_RESTART_POLICY
    objref:
      kind: Deployment
      name: my-deployment
      apiVersion: apps/v1
    fieldref:
      fieldpath: spec.template.spec.restartPolicy
```

```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
generatorOptions:
  # labels to add to all generated resources
  labels:
    kustomize.generated.resources: somevalue
  # annotations to add to all generated resources
  annotations:
    kustomize.generated.resource: somevalue
  # disableNameSuffixHash is true disables the default behavior of adding a
  # suffix to the names of generated resources that is a hash of
  # the resource contents.
  disableNameSuffixHash: true
```
