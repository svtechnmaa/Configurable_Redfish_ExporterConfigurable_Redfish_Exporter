from fastapi import FastAPI, Depends
from .routers import prometheus,generator
import uvicorn
# import logging
import argparse
from os import path,makedirs

app = FastAPI(title="Redfish Collector", description="Redfish DMTF Collector using for physical server monitoring")
app.include_router(prometheus.router)
app.include_router(generator.router)

# settings = Settings()

def main():
    parser = argparse.ArgumentParser(description='Physical Server state Exporter for Prometheus')

    parser.add_argument('--host', type=str, dest='host', default='0.0.0.0', help='address to serve on')
    parser.add_argument('--port', type=int, dest='port', default=9814, help='port to bind')
    parser.add_argument('--templatedir', type=str, dest='templatedir', help='Directory Configs')
    parser.add_argument('--datadir', type=str, dest='datadir', help='Directory Data Old and New saved')

    args = parser.parse_args()
    config_path = path.join(path.dirname(__file__), 'logging/logging.yml')

    if args.host:
        host = args.host
    if args.port:
        port = args.port
    if args.templatedir:
        template_dir = args.templatedir
    if args.datadir:
        data_dir = args.datadir

    uvicorn.run("redfish_collector.main:app", host=host, port=port, log_config=config_path)


if __name__ == "__main__":
    main()
