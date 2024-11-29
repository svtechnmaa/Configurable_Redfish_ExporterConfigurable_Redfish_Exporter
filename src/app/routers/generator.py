from os import path,makedirs
import yaml
from ..core.dataReconstruction import dataReconstructor
from ..core.rawCollector import jsonpathCollector,dataCollector
from concurrent.futures import ThreadPoolExecutor,ProcessPoolExecutor
from multiprocessing import Process
from fastapi import APIRouter, Depends
import time
import logging
import asyncio
# from ..main import get_settings
# from ..config import Settings
# settings = Settings()
# templateDir = settings.TEMPLATE_DIR
# inventoryDir= settings.TEMPLATE_DIR + 'configs/inventory.yml'


router = APIRouter(
    tags=['Core Processor']
)

def redfishCollector(serverAddress,username,password):
    templateDir = config_path = path.join(path.dirname(__file__), '../core/templates/')
    # logging.info("Gathering...")
    logLevel='info'
    try:
        dataRaw, dataNewSchema, modelSchemaDir = asyncio.run(dataCollector(serverAddress,username,password,templateDir,logLevel))
        cleaned_data = dataReconstructor(dataRaw, dataNewSchema, modelSchemaDir, serverAddress,logLevel)
    except Exception as err:
        logging.error("[%s] Tried collecting data failed: %s" %(serverAddress,err))
    # logging.info("Generate finished")
    return

def start_background_thread():
    while True:
        # templateDir + "schemas/Common.yml"
        # logging.info("Checking")
        # inventoryDir='app/core/templates/configs/inventory.yml'
        inventoryDir = path.join(path.dirname(__file__), '../core/templates/configs/inventory.yml')
        # if path.isfile(config_file_path):
        try:
            with open(inventoryDir, 'r') as f:
                yamlContent = f.read()
                inventory = yaml.safe_load(yamlContent)
        except Exception as err:
            logging.error("Read Inventory Configs failed: %s" %err)
        
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(redfishCollector, server['serverAddress'], server['username'], server['password']) for server in inventory]
        time.sleep(60)

# Start the background thread on app startup
@router.on_event("startup")
async def startup_event():
    # inventoryDir= templateDir + 'configs/inventory.yml'
    # Start the background process to collect data
    # # process = get_context("spawn")
    try:
        process = Process(target=start_background_thread)
        # process.daemon=True
        process.start()
    except KeyboardInterrupt:
        print("KeyboardInterrupt caught in process.")
    finally:
        print("Process is shutting down gracefully.")