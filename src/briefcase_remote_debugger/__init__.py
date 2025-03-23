import json
import os
from typing import TypedDict

REMOTE_DEBUGGER_STARTED = False

class PathMappings(TypedDict):
    app_folder_device_regex: str
    app_subfolders_device: list[str]
    app_subfolders_host: list[str]

    app_packages_folder_device_regex: str
    app_packages_folder_host: str


class RemoteDebuggerConfig(TypedDict):
    mode: str  # client / server
    ip: str
    port: int
    path_mappings: PathMappings

def start_remote_debugger():
    global REMOTE_DEBUGGER_STARTED
    REMOTE_DEBUGGER_STARTED = True

    # Reading and parsing config
    config = os.environ.get("BRIEFCASE_REMOTE_DEBUGGER", None)
    if config is None:
        # If BRIEFCASE_REMOTE_DEBUGGER is not set, this packages does nothing...
        return

    print("Found BRIEFCASE_REMOTE_DEBUGGER:")
    print(json.dumps(config,indent=4))
    config: RemoteDebuggerConfig = json.loads(config)

    # Starting selected debugger
    if config["debugger"] == "pdb":
        import briefcase_remote_debugger.pdb
        briefcase_remote_debugger.pdb.start_pdb(config)
    elif config["debugger"] == "debugpy":
        import briefcase_remote_debugger.debugpy
        briefcase_remote_debugger.debugpy.start_debugpy(config)
    
# only start remote debugger on the first import
if REMOTE_DEBUGGER_STARTED == False:
    start_remote_debugger()