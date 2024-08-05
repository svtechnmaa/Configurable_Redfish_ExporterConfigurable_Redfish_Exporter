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
