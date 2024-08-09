"""
Entrypoint for the application
"""

import argparse
from redfish_exporter.prometheusExporter import prometheusExporter

def main():
    parser = argparse.ArgumentParser(description='Physical Server state Exporter for Prometheus')

    parser.add_argument('--address', type=str, dest='address', default='0.0.0.0', help='address to serve on')
    parser.add_argument('--port', type=int, dest='port', default='9814', help='port to bind')
    parser.add_argument('--endpoint', type=str, dest='endpoint', default='/metrics', help='endpoint where metrics will be published')
    parser.add_argument('--loglevel', type=str, dest='loglevel', default="info", help='log level used for debugging')
    parser.add_argument('--templatedir', type=str, dest='templatedir', default='/opt/Configurable_Redfish_Exporter/templates/', help='cache timeout for renew request')

    args = parser.parse_args()

    exporter = prometheusExporter(**vars(args))
    exporter.run()

if __name__ == '__main__':
    main()