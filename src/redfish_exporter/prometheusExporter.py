import time
import logging
import yaml
import json
from os import path
from jsonpath_ng.ext import parse 
from jinja2 import Template
from yaml.loader import SafeLoader
from threading import Thread
from http.server import SimpleHTTPRequestHandler
from socketserver import ThreadingMixIn,TCPServer
from redfish_exporter.dataReconstruction import dataReconstruction
from prometheus_client import generate_latest, Summary, REGISTRY, PROCESS_COLLECTOR, PLATFORM_COLLECTOR, Gauge, CollectorRegistry
from urllib.parse import parse_qs
from urllib.parse import urlparse
import re

REGISTRY.unregister(PROCESS_COLLECTOR)
REGISTRY.unregister(PLATFORM_COLLECTOR)
REGISTRY.unregister(REGISTRY._names_to_collectors['python_gc_objects_collected_total'])
# registry = REGISTRY

REQUEST_TIME = Summary(
    'request_processing_seconds', 'Time spent processing request')
CACHE={}

def readYAMLTemplate(templateFile, dynamicInput):
    config_file_path = path.join(path.dirname(__file__), templateFile)
    if path.isfile(config_file_path):
        with open(templateFile, 'r') as f:
            yamlContent = f.read()
            renderedContent = Template(yamlContent).render(dynamicInput)
            configData = yaml.safe_load(renderedContent)
            logging.debug("Component Schema Data: %s" % (configData))
            return configData
    else:
        logging.error("Can not find: %s" % (templateFile))
        return

def jsonpathCollector(content,expression,output='value'):
    jsonpath_expr = parse(str(expression))
    if output == 'fullpath&value':
        result = dict()
        for match in jsonpath_expr.find(content):
            result[str(match.full_path)] = match.value
        return result
    else:
        result = [match.value for match in jsonpath_expr.find(content)]
        if result == []:
            return False
        else:
            return result

class ThreadedTCPServer(ThreadingMixIn,TCPServer):
    pass

class ManualRequestHandler(SimpleHTTPRequestHandler):
    """
    Endpoint handler
    """
    def log_message(self, format, *args):
        pass

    def _sendContent(self, data, status=200, content_type="text/plain"):
        if isinstance(data, str):
            data = data.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)
        self.wfile.flush()

    def do_GET(self):
        start_time = time.time()
        url = urlparse(self.path)
        logging.debug(url)
        if url.path == "/":
            return self._sendContent(
                "<form method=get action=/data><input type=search name=q><input type=submit></form>",
                content_type="text/html",
            )
        elif url.path == self.endpoint:
            qs = parse_qs(url.query)

            serverAddress = None
            # redfishPort = 443
            username = None
            password = None
            try:
                serverAddress = qs['serverAddress'][0]
                # redfishPort = int(query_components['port'][0])
                username = qs['username'][0]
                password = qs['password'][0]
                config = qs['config'][0]
                cacheTimeout = qs['cachetimeout'][0]
                # logging.info("Username: %s: %s" % (username,serverAddress))
                logging.info("[%s] Received prometheus query from %s to gather health-check information" % (serverAddress,str(self.address_string())))
            except KeyError as e:
                logging.error("[%s] Missing parameter %s" % (serverAddress, e))
                return self._sendContent(f"404: {url}", status=404)

            cacheInfo="%s%s%s" % (serverAddress,username,password)
            if cacheInfo in CACHE:
                cachedResponse, timestamp = CACHE[cacheInfo]
                if time.time() - timestamp < int(cacheTimeout):
                    logging.info("[%s] Complete gathering health-check information from cache", serverAddress)
                    return self._sendContent(cachedResponse, content_type="application/json")

            dataraw, collectedData=dataReconstruction(serverAddress,username,password,self.templatedir,self.loglevel)
            logging.info("[%s] Complete gathering health-check information", serverAddress)
            hostName = collectedData['Common']['HostName']

            metricsConfigFile = self.templatedir + "configs/" + config + ".yml"
            metricsConfig = readYAMLTemplate(metricsConfigFile, {'serverAddress': serverAddress})
            logging.debug("[%s] Yaml Config Metrics Content: %s" % (serverAddress, metricsConfig))

            # componentMetrics = list()
            registry = CollectorRegistry()
            componentMetrics={}
            # registry.clear()
            for metric in metricsConfig['Metrics']:
                standard = ['Name', 'Description', 'Label', 'Datapoint', 'Result', 'Type']
                errorFlag = 0
                for key in standard:
                    # logging.info("[%s] Key: %s" % (serverAddress, key))
                    if key not in metric:
                        logging.error("[%s] Can't find %s in metrics key, please check again!" % (serverAddress, key))
                        errorFlag = 1
                if errorFlag == 1:
                    continue
                else:
                    if metric['Type'] == 'Gauge':
                        componentMetrics[metric['Name']] = Gauge(metric['Name'],metric['Description'],metric['Label'],registry=registry)
                        elements = metric['Datapoint'].split('.')
                        logging.info("[%s] Split datapoint %s to %s" % (serverAddress,metric['Datapoint'],elements))
                        if isinstance(elements,list):
                            firstPointData = collectedData
                        else:
                            logging.error("[%s] Elements after splited isn't a list: %s" % (serverAddress,elements))
                            continue
                        # logging.error("Fist Point: %s" % firstPointData)
                        idList = jsonpathCollector(firstPointData,str("$..Id"),output='fullpath&value')
                        for memberID in idList:
                            if elements[-1] in memberID and elements[0] in memberID:
                                labelList = list()
                                for label in metric['Label']:
                                    if label == 'ServerAddress':
                                        labelList.append(serverAddress)
                                    elif label == 'HostName':
                                        labelList.append(hostName)
                                    else:
                                        newJSONPath = re.sub('Id', label, memberID)
                                        result = jsonpathCollector(firstPointData,newJSONPath)
                                        if result is not False:
                                            labelList.append(result[0])
                                        else:
                                            labelList.append('Unknown')
                                            continue
                                logging.debug("[%s] List Label: %s" % (serverAddress,labelList))
                                if 'State' in metric['Result'] or 'Health' in metric['Result']:
                                    if 'StatusCode' not in metric:
                                        logging.error("[%s] Can't find StatusCode, please check again!" % (serverAddress))
                                        continue
                                    state = 'Status.' + metric['Result']
                                    newJSONPath = re.sub('Id', state, memberID)
                                    logging.debug("[%s] newJSONPath: %s" % (serverAddress,newJSONPath))
                                    value = jsonpathCollector(firstPointData,str(newJSONPath))
                                    if value is False:
                                        logging.error("[%s] Value isn't existed: %s" % (serverAddress,value))
                                        codeNumber = 999
                                    elif value is None:
                                        logging.warning("[%s] Value is None: %s" % (serverAddress,value))
                                        codeNumber = 99
                                    elif value[0] is None:
                                        logging.warning("[%s] Value[0] is None: %s" % (serverAddress,value[0]))
                                        codeNumber = 99
                                    else:
                                        if value[0].upper() in metric['StatusCode']:
                                            codeNumber = metric['StatusCode'][value[0].upper()]
                                            logging.info("[%s] Value and CodeNumber: %s and %s" % (serverAddress,value,codeNumber))
                                        else:
                                            logging.error("[%s] Maybe value isn't correct: %s" % (serverAddress,value))
                                            codeNumber = 999
                                    componentMetrics[metric['Name']].labels(*labelList).set(float(codeNumber))
                                else:
                                    newJSONPath = re.sub('Id', metric['Result'], memberID)
                                    value = jsonpathCollector(firstPointData,str(newJSONPath))
                                    if value is False:
                                        componentMetrics[metric['Name']].labels(*labelList).set(999)
                                    else:
                                        value =value[0]
                                    logging.debug("Value type: %s" % type(value))
                                    if isinstance(value,int) or isinstance(value,float):
                                        componentMetrics[metric['Name']].labels(*labelList).set(float(value))       
                                    else:
                                        logging.error("[%s] Value %s isn't float: %s" % (serverAddress,metric['Result'],value))
                                        componentMetrics[metric['Name']].labels(*labelList).set(999)   
                                logging.info("[%s] ID List Collected with in tree %s to %s" % (serverAddress,metric['Datapoint'],labelList))    
                            # else: 
                            #     logging.error("[%s] elements[-1] %s and elements[0] %s and memberID %s " % (serverAddress,elements[-1],elements[0],memberID))
                    else:
                        logging.error("[%s] Not found Type %s, please call Admin" % (serverAddress, i['Type']))

            metrics = generate_latest(registry)
            REQUEST_TIME.observe(time.time() - start_time)
            CACHE[cacheInfo] = (metrics, time.time())
            return self._sendContent(metrics, content_type="application/json")
        else:
            return self._sendContent(f"404: {url}", status=404)

class prometheusExporter(object):
    """
    Basic server implementation that exposes metrics to Prometheus
    """

    def __init__(self, address='0.0.0.0', port=8080, endpoint="/metrics", loglevel="info", templatedir="/opt/src/nextgen/templates/"):
        self._address = address
        self._port = port
        self._endpoint = endpoint
        self._loglevel = loglevel.upper()
        self._templatedir = templatedir
        # self._cachetimeout = cachetimeout

    def run(self):
        logging.basicConfig(format='%(asctime)s [%(levelname)s] %(message)s', level=(self._loglevel).upper())
        with ThreadedTCPServer(("", self._port), ManualRequestHandler) as httpd:
            ManualRequestHandler.endpoint=self._endpoint
            ManualRequestHandler.loglevel=self._loglevel
            ManualRequestHandler.templatedir=self._templatedir
            try:
                logging.info("Serving at port " + str(self._port))
                threadServer=Thread(httpd.serve_forever())
                threadServer.daemon()
                threadServer.start()
            except KeyboardInterrupt:
                httpd.shutdown()
                logging.info("Killed exporter Successfully")