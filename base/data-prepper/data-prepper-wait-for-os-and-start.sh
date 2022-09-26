#!/bin/bash
until [[ $(curl --write-out %{http_code} --output /dev/null --silent --head --fail https://opensearch-cluster-master:9200 -u admin:admin --insecure) == 200 ]]; do
    echo "Waiting for OpenSearch to be ready"
    sleep 1
done
java -Xms128m -Xmx128m -jar /usr/share/data-prepper/data-prepper.jar /appconfig/log-ssl.yml