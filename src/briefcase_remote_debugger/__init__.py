import json
import os
import sys
import traceback
from typing import TypedDict

REMOTE_DEBUGGER_STARTED = False

class AppPathMappings(TypedDict):
    device_sys_path_regex: str
    device_subfolders: list[str]
    host_folders: list[str]

class AppPackagesPathMappings(TypedDict):
    sys_path_regex: str
    host_folder: str

class RemoteDebuggerConfig(TypedDict):
    debugger: str
    mode: str  # client / server
    ip: str
    port: int
    app_path_mappings: AppPathMappings | None
    app_packages_path_mappings: AppPackagesPathMappings | None

def start_remote_debugger():
    global REMOTE_DEBUGGER_STARTED
    REMOTE_DEBUGGER_STARTED = True

    # Reading and parsing config
    config = os.environ.get("BRIEFCASE_REMOTE_DEBUGGER", None)
    if config is None:
        # If BRIEFCASE_REMOTE_DEBUGGER is not set, this packages does nothing...
        return

    print("Found BRIEFCASE_REMOTE_DEBUGGER config:")
    config: RemoteDebuggerConfig = json.loads(config)
    print(json.dumps(config,indent=4))

    # Starting selected debugger
    if config["debugger"] == "pdb":
        import briefcase_remote_debugger.pdb
        briefcase_remote_debugger.pdb.start_pdb(config)
    elif config["debugger"] == "debugpy":
        import briefcase_remote_debugger.debugpy
        briefcase_remote_debugger.debugpy.start_debugpy(config)
    
# only start remote debugger on the first import
if REMOTE_DEBUGGER_STARTED == False:
    try:
        start_remote_debugger()
    except Exception as e:
        # Show exceiption and stop the whole application when an error occures
        print(traceback.format_exc())
        sys.exit(-1)