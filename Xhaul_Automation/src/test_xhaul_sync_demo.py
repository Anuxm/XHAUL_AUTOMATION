import time
import pytest
import allure
import sys
import os
import yaml
 
sys.path.insert(0,
                os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
ABSOLUTE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../'))
 
from lib.common.constant import *
from lib.connection.connection_api import SSHConnection
from lib.common.utils import Utils
from lib.log.custom_log import *
from validation.validation import Validate
from helper.setup import XhaulSetup
 
LOG = Logger(__name__)
 
file_name = None
sys_list = sys.argv[1:]
 
LOG.log_title("updating the inventory yaml file based on user preferences, "
              "using either static or dynamic data")
res = XhaulSetup().updating_inventory_params(sys_args_list=sys_list)
if res:
    LOG.log_info("Inventory file is updated with appropriate details")
       
 
gui_config = f"{ABSOLUTE_PATH}/resources/inventory_params.yaml"
gui_data = yaml.load(open(gui_config), Loader=yaml.FullLoader)
 
falcon_tc_config = f"{ABSOLUTE_PATH}/resources/tc_config_params.yaml"
tc_config_data = yaml.load(open(falcon_tc_config), Loader=yaml.FullLoader)
tc_config = tc_config_data['TC_Config_Params']
 
weblink = gui_data['Dynamic_Params']['baseUrl']
gui_server_ip = gui_data['Dynamic_Params']['Server']['serverIp']
gui_server_port = gui_data['Dynamic_Params']['Server']['serverPort']
target_server_ip = gui_data['Dynamic_Params']['Target_Server1']['targetIp']
target_ip_user = gui_data['Dynamic_Params']['Target_Server1']['username']
target_ip_pwd = gui_data['Dynamic_Params']['Target_Server1']['password']
script_path = gui_data['Dynamic_Params']['ffpath']
falcon_cmd = tc_config['test_falcon_tc1']['mainfal_cmd']
 
 
@pytest.mark.gui_based
@pytest.mark.parametrize("tc_name", ["test_falcon_gui_test"])
def test_falcon_gui_test(browser, tc_name):
    """
    This test_falcon_gui_test is a testcase to check following senarios
    1. Starting mainfalcon
    2. Enable HTTP
    3. Enable RPC
    3. Take ACM Microwave status
    :param : browser: It is a instance of browser
    :param : tc_name: Name of the testcase
    """
    LOG.log_title("Testcase Description")
    LOG.log_info("This test_falcon_gui_test is a testcase to check following "
                 "senarios "
                 "1. Starting mainfalcon"
                 "2. Enable HTTP"
                 "3. Enable RPC"
                 "4. Take ACM Microwave status")
    global file_name
    result = []
    # cli based functionality
 
    LOG.log_title(f"Login to soc card via ssh with ip {target_server_ip}")
    con_obj_soc = SSHConnection(ip=target_server_ip, username=target_ip_user,
                                password=target_ip_pwd)
    LOG.log_title("Verifying whether the Main Falcon is running or not")
    main_falcon_process_list = Utils().get_process_id(process_name="mainfalcon",
                                                      con_obj=con_obj_soc)
    time.sleep(TIME_3S)
    LOG.log_info(main_falcon_process_list)
    if len(main_falcon_process_list) > 1:
        LOG.log_info("The mainfalcon is already active.")
    else:
        LOG.log_title("Since mainfalcon is not currently in an active state, "
                      "start mainfalcon in SOC.")
        mainfolcon_op = con_obj_soc.exec_command(command=falcon_cmd,
                                                 resp_time=TIME_20S)
        time.sleep(TIME_5S)
        LOG.log_title("Confirming if mainfalcon has started or not")
        if mainfolcon_op.find("rpc_server() started...") != -1:
            LOG.log_info("Mainfolcon launched succesfully.")
            result.append(True)
        else:
            LOG.log_error("Mainfalcon fails to launch successfully.")
            result.append(False)
 
    LOG.log_title("Accessing falcon GUI")
    time.sleep(TIME_5S)
    # gui based functionality
    page = browser.new_page()
    page.goto(weblink)
    page.wait_for_timeout(time_3s)
    # validation1:
    LOG.log_title("Checking to see whether the falcon gui has loaded")
    home_page_selector = "body > app-root > div > app-header > div > " \
                         "div.title > span > b"
    element = page.query_selector(home_page_selector)
    rst1 = Validate().validate_page_load(element, "falcon gui page")
    result.append(rst1)
    if rst1:
        LOG.log_title("capturing a screenshot of the falcon gui before the "
                      "connection for HTTP and RPC")
        page.screenshot(
            path=f"output/screenshot/{tc_name}_http_rpc_status1.png")
 
        LOG.log_title("Determining whether HTTP and RPC are connected or not")
        http_title1 = page.get_by_title("HTTP Disconnected (1.10.5)")
        rpc_title1 = page.get_by_title("RPC Disconnected")
        if http_title1 and rpc_title1:
            LOG.log_info("Please reconnect to HTTP and RPC because it is "
                         "currently disconnected.")
            LOG.log_title("Connecting to the HTTP")
            page.get_by_role("button", name="Configuration").click()
            page.wait_for_timeout(time_3s)
            page.get_by_role("menuitem", name="Connect GUI to Server").click()
            page.wait_for_timeout(time_3s)
            LOG.log_title("Verifying whether the HTTP server configuration "
                          "window is loaded or not")
            srv_conf_setting = "#mat-dialog-0 > app-backend-configuration > " \
                               "mat-toolbar"
            element = page.query_selector(srv_conf_setting)
            rst2 = Validate().validate_page_load(element, "Server configuration"
                                                          " page")
            result.append(rst2)
            if rst2:
                LOG.log_info(f"Updating {gui_server_ip} in host_ip to connect "
                             f"to HTTP")
                page.locator("#serverConfigIpId").click()
                page.locator("#serverConfigIpId").fill(gui_server_ip)
                page.wait_for_timeout(time_2s)
 
                LOG.log_info(
                    f"Updating {gui_server_port} in host ip to connect "
                    f"to HTTP")
                page.locator("#serverConfigPortId").click()
 
                page.locator("#serverConfigPortId").fill(gui_server_port)
                page.wait_for_timeout(time_2s)
                page.get_by_role("button", name="OK").click()
                LOG.log_title("Checking whether HTTP is connected or not")
                http_title2 = page.get_by_title("HTTP Connected (1.10.5)")
                if http_title2:
                    LOG.log_info("HTTP is connected succesfully")
                    result.append(True)
                else:
                    LOG.log_error("Http is not connected succesfully")
                    result.append(False)
            else:
                LOG.log_error("The Server Configuration Settings window has "
                              "not successfully loaded when attempting to "
                              "connect to HTTP.")
            LOG.log_title("Connecting to the RPC")
            page.goto(weblink)
            page.wait_for_timeout(time_5s)
            page.get_by_role("button", name="Configuration").click()
            page.wait_for_timeout(time_3s)
            page.get_by_role("menuitem", name="Connect Server to Target"). \
                click()
            page.wait_for_timeout(time_3s)
            LOG.log_title("Validating whether Target configuration settings "
                          "window is loaded or not to connect to RPC")
            target_conf_setting = "#mat-dialog-0 > app-target-configuration " \
                                  "> mat-toolbar"
            element = page.query_selector(target_conf_setting)
            rst3 = Validate().validate_page_load(element, "Target configuration"
                                                          " page")
            result.append(rst3)
            LOG.log_title("Modifying soc ip in the Target server settings for "
                          "connecting RPC")
            page.locator("#targetNearEndId").click()
            page.locator("#targetNearEndId").press("ArrowRight")
            page.locator("#targetNearEndId").fill(target_server_ip)
            page.wait_for_timeout(time_3s)
            page.get_by_role("button", name="OK").click()
 
            LOG.log_title("Determining whether RPC is connected or not")
            rpc_title2 = page.get_by_title("RPC Connected")
            if rpc_title2:
                LOG.log_info("RPC is connected succesfully")
                result.append(True)
            else:
                LOG.log_error("RPC connection is unsuccessful")
            LOG.log_title("Capturing screenshot after connecting to HTTP and "
                          "RPC")
            screenshot1 = page.screenshot(
                path=f"output//screenshot//{tc_name}_http_rpc_"
                     f"status2.png")
            allure.attach(screenshot1,
                          name=f"output//screenshot//{tc_name}_http_rpc_"
                               f"status2.png",
                          attachment_type=allure.attachment_type.PNG)
 
            LOG.log_title("Uploading script to configure soc")
            page.locator("mat-tree-node").filter(
                has_text="chevron_right Utils").click()
            page.get_by_label("toggle Utils").click()
            page.get_by_label("toggle Ch0").click()
            page.get_by_role("button", name="- Script upload").click()
 
            #dir_path = f"{ABSOLUTE_PATH}\\resources\\acm_status_content.txt"
            profile_file = tc_config['test_falcon_tc1']['profile_name']
            dir_path = f"{script_path}//{profile_file}"
            with page.expect_file_chooser() as fc_info:
                page.get_by_title("Open script file").click()
            file_chooser = fc_info.value
            file_chooser.set_files(dir_path)
            page.wait_for_timeout(time_3s)
 
            page.get_by_role("button", name="Send", exact=True).click()
            page.wait_for_timeout(time_5s)
            page.locator('body > app-root > div > div > div.tabs-container > '
                         'div > app-panel:nth-child(31) > div > div.pheader.'
                         'cdk-drag-handle > div.pclose.piconize > i').click()
            page.wait_for_timeout(time_3s)
 
            LOG.log_title("Following successful HTTP and RPC connection, "
                          "obtaining the ACM status")
            LOG.log_title("Selecting Modem option")
            page.get_by_label("toggle Modem").click()
            page.locator("button").filter(has_text="chevron_right Ch0 - "
                                                   "Microwave").click()
            page.wait_for_timeout(time_5s)
            page.get_by_role("button", name="- ACM").click()
            page.wait_for_timeout(time_3s)
            LOG.log_title("Verifying whether ACM Microwave window get "
                          "opened or not")
            acm_microwave = "body > app-root > div > div > div.tabs-container " \
                            "> div > app-panel:nth-child(1) > div > " \
                            "div.pheader.cdk-drag-handle"
            element = page.query_selector(acm_microwave)
            rst4 = Validate().validate_page_load(element, "acm_microwave")
            result.append(rst4)
            if rst4:
                # page.get_by_role("cell",
                #                  name="TX PHY Mode keyboard_arrow_up "
                #                       "keyboard_arrow_down Auto Man. RX PHY "
                #                       "Mode PHY 0 4qam").locator("label").click()
                #
                # page.wait_for_timeout(time_5s)
                mse_value = page.locator('#mseDivId').text_content()
                if round(float(mse_value)) > 48:
                    LOG.log_info(f"Generated valid mse value as {mse_value}")
                    result.append(True)
                else:
                    LOG.log_error(f"generated invalid mse value as {mse_value}")
                    result.append(False)
                LOG.log_info("Minimizing the window to capture a "
                             "better screenshot")
                page.evaluate('document.body.style.zoom = "75%";')
                page.wait_for_timeout(time_3s)
                LOG.log_info("Capturing a screenshot of the ACM status to "
                             "include in the HTML report.")
                file_name = f"{tc_name}_ACM.png"
                screenshot2 = page.screenshot(path=f"output\{file_name}",
                                              full_page=True)
                allure.attach(screenshot2, name=f"output\{file_name}",
                              attachment_type=allure.attachment_type.PNG)
 
            else:
                LOG.log_error("Having trouble to load the ACM Microwave window")
 
        else:
            server_ip = page.query_selector("#serverConfigIpId").text_content()
            server_port = page.query_selector("#serverConfigPortId"). \
                text_content()
            target_ip = page.query_selector("#targetNearEndId").text_content()
            LOG.log_info(f"HTTP and RPC is already connected with server ip "
                         f"is :{server_ip} , server port is: {server_port} "
                         f"and target ip is :{target_ip} please Continue ...")
    else:
        LOG.log_error("Unable to connect to Falcon gui")
        result.append(False)
    page.close()
    Utils().get_test_result(all(result), tc_name)
 
