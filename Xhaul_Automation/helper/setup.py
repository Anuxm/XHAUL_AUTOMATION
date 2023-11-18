import yaml
import sys
import os
 
 
sys.path.insert(0,
                os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
ABSOLUTE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../'))
 
from lib.log.custom_log import *
 
LOG = Logger(__name__)
 
inventory_path = f"{ABSOLUTE_PATH}/resources/inventory_params.yaml"
 
# we can pass gui link,
class XhaulSetup:
    """
    This XhaulSetup class is a place holder for methods which are used to setup
    all configurations before test execution
    """
 
    def __int__(self):
        pass
 
    def updating_inventory_params(self, sys_args_list: list) -> bool:
        """
        This updating_inventory_params method is used to update inventory yaml
        file as per command line interface otherwise it can take default
        arguments
        :param : sys_args_list: This is a list which contains all sys arguments
        :type : sys_args_list: list
        :return: True/False
        : raises: FileNotFoundError and IOError
        """
        try:
            result = []
            with open(inventory_path, 'r') as file:
                data = yaml.safe_load(file)
            if not data:
                raise FileNotFoundError("Failed to load inventory data from "
                                        "the file.")
            if '--params_type' in sys_args_list[1:]:
                params_index = sys_args_list.index('--params_type')
                if params_index < len(sys_args_list) - 1:
                    param_type = sys_args_list[params_index + 1]
                    inventory_data = data.get('Dynamic_Params')
                    default_data = data.get('Static_Params')
                    if not inventory_data or not default_data:
                        raise IOError(
                            "Inventory data is missing in the YAML file.")
                    if 'dynamic' in param_type:
                        arg_list = ['--baseurl', '--server_ip',
                                    '--server_port', '--target_ip',
                                    '--epic_ip', '--script_path']
                        self._update_inven_with_dynamic_args(arg_list,
                                                             sys_args_list,
                                                             inventory_data)
                    elif 'static' in param_type:
                        self._update_inven_with_static_args(inventory_data,
                                                            default_data)
                        result.append(True)
                    else:
                        raise IOError(
                            "Given params_type is invalid.")
                else:
                    raise IOError(
                        "Missing a value for '--params_type' argument.")
            else:
                LOG.log_error("The parameters we must pass, such as static or "
                              "dynamic, are not clearly specified.")
 
            with open(inventory_path, 'w') as file:
                yaml.dump(data, file, default_flow_style=False)
            return all(result)
        except FileNotFoundError as e:
            LOG.log_error(f"No file found with name {inventory_path}")
            return False
 
    def _update_inven_with_dynamic_args(self, arg_list, sys_list,
                                        inventory_data):
        """
        _update_inven_with_topo_args method is used to update inventory yaml if
        topology is not default
        :param arg_list: arg_list is a list which contains what are the
          what are maximum no.of addorptions we are passing in command line
        :type arg_list: list
        :param sys_list: This is a list which an hold all arguments which we are
         passing and with values in command line
        :type sys_list: list
        :param inventory_data: It is a dictionary which contains all xhaul
         inventory data
        :type inventory_data: dict
        :return: True/false
        raises: IOError : If we can pass invalid parameters to this method
        """
        result = False
        if len(arg_list) != 0 or len(sys_list) != 0:
            for arg_name in arg_list:
                if arg_name in sys_list[1:]:
                    arg_index = sys_list.index(arg_name)
                    if arg_index < len(sys_list) - 1:
                        arg_value = sys_list[arg_index + 1]
                        if arg_name == '--baseurl':
                            inventory_data['baseUrl'] = arg_value
                        elif arg_name == '--server_ip':
                            inventory_data['Server']['serverIp'] = arg_value
                        elif arg_name == '--server_port':
                            inventory_data['Server']['serverPort'] = arg_value
                        elif arg_name == '--target_ip':
                            inventory_data['Target_Server1']['targetIp'] = \
                                                                     arg_value
                        elif arg_name == '--epic_ip':
                            inventory_data['Target_Server2']['epicIp'] = arg_value
                        elif arg_name == '--script_path':
                            inventory_data['ffpath'] = arg_value
            result = True
        else:
            raise IOError("one of given parameter list or both list are empty")
        return result
 
    def _update_inven_with_static_args(self, inventory_data, default_data):
        """
        _update_inven_with_default_args method is used to update inventory yaml
        if topology is default
        :param: inventory_data: This is a type of dictionary contains inventary
        data for dynamic update
        :type inventory_data: dict
        :param default_data: This is a type of dictionary contains inventary
        data for static update
        :type default_data: dict
        :return: None
        :raises: IOError if we can pass invalid parameters
        """
        if len(inventory_data) != 0 and len(default_data) != 0:
            inventory_data['baseUrl'] = default_data['baseUrl']
            inventory_data['Server']['serverIp'] = \
                default_data['Server']['serverIp']
            inventory_data['Server']['serverPort'] = \
                default_data['Server']['serverPort']
            inventory_data['Target_Server1']['targetIp'] = \
                default_data['Target_Server1']['targetIp']
            inventory_data['Target_Server2']['epicIp'] = \
                default_data['Target_Server2']['epicIp']
            inventory_data['ffpath'] = default_data['ffpath']
        else:
            raise IOError("Invalid parameters passed")
 
 
if __name__ == "__main__":
    pass