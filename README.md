# Configurable Redfish Exporter
The End goal is a Prometheus exporter that can automatically create server metric base on Redfish API and JSON Metric mapping configuration
Folder structure should as follow:
- source code
- configuration file for mapping logic from individual vendor to common YAML/JSON schema
- configuration file for mapping logic from common YAML/JSON schema to exporter metric
- deployment files

### Version: 1.0 
Date: 24/07/2024
Maintainer: Freezing
Finally, the first version created with many issues (I think so :D), include:
- Schemas: Define new data model from old data collected by Redfish API (HPEiLO/iDRAC)
- Configs: Define metrics collection for prometheus exporter
Guide:
- Run main.py with --arg

Anyway, Cheers!
