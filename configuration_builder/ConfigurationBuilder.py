# -*- coding: utf-8 -*-
#
# Configuration builder allow make app configuration
# Author: Klabukov Erik <amest00@gmail.com>
#

import os
import json
import subprocess
from pathlib import Path

class ConfigurationBuilder(object):
    """
    Configuration builder that allows you to build configurations as Microsoft.Extension.Configuration
    merge the main application settings (appsettings.json) with another json document, environment variables
    or getting configurations from dotnet user-secrets
    """
    _config = None
    
    def add_json_file(self, file_path: str = "appsettings.json", optional: bool = True) -> None:
        """ Add and merge configuration from json file """
        if(not os.path.exists(file_path) and optional):
            return
        loaded_config = self.__load_configuration_from_file(file_path)
        self.__add_config(loaded_config)

    def add_environment_variables(self) -> None:
        """ Add and merge configuration from environment variable"""
        loaded_config = self.__load_configuration_from_env()
        self.__add_config(loaded_config)

    def add_user_secrets(self, id: str = None) -> None:
        """ Add and merge configuration from dotnet user-secrets"""
        if(id is None):
            id = self.__find_usersecrets_id()
        if(id is None or id == ""):
            print("File `.usersecrets` with id not found")
            return
        loaded_config = self.__load_configuration_from_usersecrets(id)
        self.__add_config(loaded_config)

    def build(self) -> dict:
        """ Return complete version of configuration """
        return self._config
    
    def __add_config(self, loaded_config: dict) -> None:
        if(self._config is None):
            self._config = loaded_config
        else:
            self._config = self.__selective_merge(self._config, loaded_config)

    def __load_configuration_from_file(self, file_name) -> dict:
        with open(file_name, 'r', encoding="utf-8") as file:
            return self.__normalize_json(json.load(file))
        
    def __load_configuration_from_env(self) -> dict:
        excluded_system_vars = ["TERM_PROGRAM","SHELL","TERM","TMPDIR", "TERM_PROGRAM_VERSION","TERM_SESSION_ID","USER","SSH_AUTH_SOCK","PATH","PWD","XPC_FLAGS","SHLVL","HOME","DISPLAY","LANG","OLDPWD"]
        environment_variables = {k: v for k,v in os.environ.items() if not k in excluded_system_vars}
        return self.__normalize_json(environment_variables)
    
    def __load_configuration_from_usersecrets(self, id) -> dict:
        dotnet_user_secrets_process = subprocess.Popen(
                ["dotnet", "user-secrets", "list", "--id", f"{id}", "--json"]
                , stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output = dotnet_user_secrets_process.communicate()[0].decode()
        output = output.replace("//BEGIN","").replace("//END","").replace("\n","")
        return self.__normalize_json(json.loads(output))
    
    def __normalize_json(self, json_dict: dict) -> dict:
        normalized_nodes = {}
        keys = list(json_dict.keys())
        for key in keys:
            delimiter = self.__detect_delimiter(key)
            if(delimiter is None):
                continue
            self.__normalize_node(normalized_nodes, delimiter, key, json_dict[key])
            del json_dict[key]
        return self.__selective_merge(json_dict, normalized_nodes)
    
    def __selective_merge(self, base_obj, delta_obj) -> dict:
        if not isinstance(base_obj, dict):
            return delta_obj
        common_keys = set(base_obj).intersection(delta_obj)
        new_keys = set(delta_obj).difference(common_keys)
        for k in common_keys:
            base_obj[k] = self.__selective_merge(base_obj[k], delta_obj[k])
        for k in new_keys:
            base_obj[k] = delta_obj[k]
        return base_obj
    
    @staticmethod
    def __normalize_node(nodes: dict, delimiter:str, key:str, value:str ) -> None:
        config_node = nodes
        key_parts = key.split(delimiter)
        for key_part in key_parts[:-1]:
            new_config_node = config_node.get(key_part)
            if new_config_node is None:
                config_node[key_part] = {}
                new_config_node = config_node[key_part]
            config_node = new_config_node
        node_key = key_parts[0] if len(key_parts) == 1 else key_parts[-1]
        if(value.isdecimal()):
            config_node[node_key] = int(value)
        elif("." in value 
            and len(value.split(".")) == 2
            and value.split(".")[0].isdecimal()
            and value.split(".")[1].isdecimal()):
            config_node[node_key] = float(value)
        else:
            config_node[node_key] = value

    @staticmethod
    def __detect_delimiter(key: str) -> str:
        for delimiter in [":","$$","__"]:
            if delimiter in key:
                return delimiter
        return None
    
    @staticmethod
    def __find_usersecrets_id(path: Path = None, iter: int = 0) -> str:
        if(iter > 2):
            return None
        if(path is None):
            path = Path.cwd()
        user_secrets_path = path.joinpath(".usersecrets")
        if(user_secrets_path.exists()):
            return user_secrets_path.read_text("utf-8").strip('\n').strip('\r')
        if(path.joinpath(".git").exists()):
            return None
        return ConfigurationBuilder.__find_usersecrets_id(path.parent, iter + 1)