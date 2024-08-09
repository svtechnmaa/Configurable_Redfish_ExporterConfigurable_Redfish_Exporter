# Configurable Redfish Exporter

The End goal is a Prometheus exporter that can automatically create server metric base on Redfish API and JSON Metric mapping configuration.

Folder structure should as follow:
- source code
- configuration file for mapping logic from individual vendor to common YAML/JSON schema
- configuration file for mapping logic from common YAML/JSON schema to exporter metric
- deployment files

## Guide:
#### Create Exporter
There're two ways that you can use Redfish-Exporter:
* Using Container Images:
  - Pull Redfish Exporter images via `docker pull` command (if you're using docker):

    ``` bash
    docker pull ghcr.io/svtechnmaa/redfish-exporter:<version>
    ```

    Run `docker run` command if you use Docker:

    ``` bash
    docker run -d --name <your exporter name> -p 9814:9814 redfish-exporter:<version> --templatedir /opt/Configurable_Redfish_Exporter/templates/
    ```

* Using main.py:
  - Comming soon :))

#### Pull metrics from Redfish Exporter
You need to have Prometheus Server or Victoria or else, change configuration on config file:
* For example:
  
    ```
    global:
      scrape_interval: 2m 
      evaluation_interval: 30s
    scrape_configs:
    - job_name: "prometheus"
      static_configs:
      - targets: ["localhost:9090"]
    - job_name: 'node_proxmox'
      scrape_interval: 3m
      scrape_timeout: 2m
      params:
        serverAddress: ['<server-idrac-or-ilo-ip>']
        username: ['<user>']
        password: ['<password>']
        cachetimeout: ['<seconds>'] # should be 200 or 300
        config: ['sample']
      static_configs:
      - targets: ["<exporter-ip>:9814"]
    ```

#### Query metrics for testing
You can use `curl` command to query server for testing data:
* For example:

    ```bash
    curl -XGET 'http://<exporter-ip>:<exporter-port>/metrics?cachetimeout=200&config=<file name in config dir>&password=<password>&serverAddress=<server-ip>&username=<username>'
    ```

#### Compare raw data with new data
As you know data collected from vendors are different models, so we need convert them to models that defined in schema.
For troubleshooting, you can go into exporter container with `/bin/sh` and check in `/tmp` directory:
* For example:

    ```bash
    docker exec exporter /bin/sh -c 'ls /tmp/'
    
    10.97.12.1_newdata.txt    10.97.12.3_newdata.txt    10.97.99.1_newdata.txt
    10.97.12.1_rawdata.txt    10.97.12.3_rawdata.txt    10.97.99.1_rawdata.txt

    docker exec exporter /bin/sh -c 'cat /tmp/10.97.99.1_rawdata.txt'

    docker exec exporter /bin/sh -c 'cat /tmp/10.97.99.1_newdata.txt'
    ```