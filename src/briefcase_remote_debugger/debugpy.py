import os
import re
import sys
from pathlib import Path

import debugpy

from briefcase_remote_debugger import RemoteDebuggerConfig


def start_debugpy(config: RemoteDebuggerConfig):
    # Parsing ip/port
    mode = config["mode"]
    ip = config["ip"]
    port = config["port"]
    app_path_mappings = config.get("app_path_mappings", None)
    app_packages_path_mappings = config.get("app_packages_path_mappings", None)

    # Parsing path mappings
    path_mappings = []
    if app_path_mappings:
        device_app_folder = next((p for p in sys.path if re.search(app_path_mappings["device_sys_path_regex"], p)), None)
        if device_app_folder:
            for app_subfolder_device, app_subfolder_host in zip(app_path_mappings["device_subfolders"], app_path_mappings["host_folders"]):
                path_mappings.append((str(Path(device_app_folder) / app_subfolder_device), app_subfolder_host))
    if app_packages_path_mappings:
        device_app_packages_folder = next((p for p in sys.path if re.search(app_packages_path_mappings["sys_path_regex"], p)), None)
        if device_app_packages_folder:
            path_mappings.append((str(Path(device_app_packages_folder)), app_packages_path_mappings["host_folder"]))
    
    # When an app is bundled with briefcase "os.__file__" is not set at runtime
    # on some platforms (eg. windows). But debugpy accesses it internally, so it
    # has to be set or an Exception is raised from debugpy.
    if not hasattr(os, "__file__"):
        os.__file__ = ""

    # Starting remote debugger...
    if mode == "client":
        print(f'''
Connecting to debugpy server at {ip}:{port}...
To create the debugpy server using VSCode add the following configuration to launch.json and start the debugger:
{{
    "version": "0.2.0",
    "configurations": [
        {{
            "name": "Briefcase: Attach (Listen)",
            "type": "debugpy",
            "request": "attach",
            "listen": {{
                "host": "{ip}",
                "port": {port}
            }}
        }}
    ]
}}
''')
    
        try:
            debugpy.connect((ip, port))
        except ConnectionRefusedError as e:
            print("Could not connect to debugpy server. Is it already started? We continue with the app...")
            return

    elif mode == "server":
        print(f'''
The debugpy server started at {ip}:{port}, waiting for connection...
To connect to debugpy using VSCode add the following configuration to launch.json:
{{
    "version": "0.2.0",
    "configurations": [
        {{
            "name": "Briefcase: Attach (Connect)",
            "type": "debugpy",
            "request": "attach",
            "connect": {{
                "host": "{ip}",
                "port": {port}
            }}
        }}
    ]
}}
''')

        debugpy.listen((ip, port), in_process_debug_adapter=True)

    # Fix path mappings
    if (len(path_mappings) > 0):
        # path_mappings has to be applied after connection is established. If no connection is
        # established this import will fail.
        import pydevd_file_utils

        pydevd_file_utils.setup_client_server_paths(path_mappings)