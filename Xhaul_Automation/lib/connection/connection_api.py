import paramiko
import time
import re
import sys
import os
import logging
 
sys.path.insert(0,
                os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
ABSOLUTE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../'))
 
from lib.log.custom_log import Logger
from lib.common.constant import *
 
LOG = Logger(__name__)
 
 
class SSHConnection:
    """
    SSHConnection class provides generic
    methods or functionalities that enable an
    User to interact with the device under test
    Note : This class supports the below combination of connections
           - Host
           - VM/Host2 Connection from host
    """
 
    def __init__(self, ip: str, username: str, password: str, **kwargs) -> None:
        """
 
        """
 
        self.ip = ip
        self.username = username
        self.password = password
        self.connect_host2 = kwargs.get('connect_host2', False)
        if self.connect_host2:
            # Check if VM/host2 dictionary info is missing
            self.host2_info = kwargs.get('host2_dict', False)
            if self.host2_info is False:
                raise ValueError(
                    "Missing VM/host2 Credentials ==> host2_dict = {host2_ip:'', "
                    "host2_user:'', host2_pwd: ''}")
            self.host2_ip = self.host2_info.get('ip', None)
            self.host2_user = self.host2_info.get('user', None)
            self.host2_pwd = self.host2_info.get('pwd', None)
            # Check if VM/host2 ip/user/pwd info is missing
            if None in (self.host2_ip, self.host2_user, self.host2_pwd):
                raise ValueError(
                    "Missing 1 of the host2 Credentials ==> host2_dict = {host2_ip:'',"
                    " host2_user:'', host2_pwd: ''}")
        # Establish Connection
        logging.getLogger("paramiko").setLevel(logging.WARNING)
        self.conn_host = paramiko.SSHClient()
        self.conn_host.load_system_host_keys()
        self.conn_host.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        error = None
        try:
            self.conn_host.connect(self.ip,
                                   username=self.username,
                                   password=self.password)
            time.sleep(TIME_3S)
            self.channel = self.conn_host.invoke_shell()
            if self.connect_host2:
                rst = self._connect_host2()
                if not rst:
                    error = "Failed to connect to the VM/host2"
        except (paramiko.AuthenticationException,
                paramiko.SSHException) as e:
            error = f"Error occurred while connecting to host via SSH : {e}"
            LOG.log_error(error)
        finally:
            if error:
                raise ConnectionError(error)
 
    def exec_command(self, command: str, resp_time: str = TIME_3S, buffer:
                     int = NUM_BYTES_10024) -> str:
        """
        exec_command method is used to execute the commands in the
        dut/vm
        :param :command: Command to be executed either in dut/vm
        :type  :command: str
        :return: output
        """
        LOG.log_info(f"EXECUTING COMMAND in {self.ip}: {command}")
        self.channel.settimeout(resp_time)
        command = f"{command}\n"
        self.channel.sendall(command.encode("utf-8"))
        time.sleep(resp_time)
        output = self.channel.recv(buffer).decode("utf-8")
        LOG.log_info(output)
        # error handling
        error_strings = ('command not found', 'error: argument',
                         'Unknown device')
        op = output.lower()
        search_results = (x.lower() in op for x in error_strings)
        if any(search_results):
            raise ValueError(f"Exeption raised while executing command")
        else:
            m0 = re.findall("([a-z0-9A-Z-=./' ':]+)\[root@localhost\s[a-z-~\]#]+", output)
            if len(m0) > 0:
                receive_output = m0[0].strip()
                return receive_output
            else:
                return output
 
    def _disconnect(self) -> None:
        """
        disconnect method to terminate SSH Connection handle
        """
   
        self.conn_host.close()
 
    def __del__(self) -> None:
        """
        destroys object when there is no reference to the object
        """
        self._disconnect()
 
    def _connect_host2(self) -> bool:
        """
        _connect_host2 is an internal method to connect to
        vm/host2 by connecting to jump host/DUT.
        return:result
        """
        result = False
        self.channel.settimeout(TIME_3S)
        t_cmd = f"ssh {self.host2_user}@{self.host2_ip} \n"
        self.channel.sendall(t_cmd.encode("utf-8"))
        time.sleep(TIME_3S)
        pwd_op = self.channel.recv(NUM_BYTES_10024).decode("utf-8")
        output = self._authentication_check(pwd_op, self.host2_pwd)
        # Check for # prompt and return True/False
        if output.find('#') != -1:
            LOG.log_info("host2/VM Access Granted!")
            result = True
        return result
 
    def _authentication_check(self, output: str, login_pwd: str) -> str:
        """
        This _authentication_check method is used check logging authentication
        :param output: Created output after executing command
        :type output: str
        :param login_pwd: It defines password for dut/VM
        :type login_pwd: str
        :return: output
        """
        if re.search("(yes/no)", output):
            # Handle Very first attempt of VM/host2 login, Add RSA Key
            self.channel.sendall(f"yes\n")
            time.sleep(TIME_3S)
            output = LOG.log_info(
                self.channel.recv(NUM_BYTES_10024).decode("utf-8"))
        if re.search("password:", output):
            # Handle wrong password with 3 attempts
            for _ in range(3):
                self.channel.sendall(f"{login_pwd}\n")
                time.sleep(TIME_3S)
                op = self.channel.recv(NUM_BYTES_10024).decode("utf-8")
                LOG.log_info(op)
                err_strs = ('Permission denied', 'Authentication failed')
                lc_op = op.lower()
                search_results = (x.lower() in lc_op for x in err_strs)
                if any(search_results):
                    raise ConnectionRefusedError("Access denied")
                else:
                    # Sucessfull login
                    LOG.log_info("Access Granted!")
                    return op
            else:
                raise ConnectionRefusedError("Connection Refused "
                                             "- Invalid Password")
        else:
            # Handle wrong username/ip
            time.sleep(TIME_3S)
            self.channel.sendall('\x1a')
            time.sleep(TIME_3S)
            op = self.channel.recv(NUM_BYTES_10024).decode("utf-8")
            raise ConnectionRefusedError("Connection Refused - Invalid ip")
 
 
if __name__ == "__main__":
    # Creating object for SSHConnection
    con_obj = SSHConnection(ip="10.190.165.210", username="root",
                            password="root123")
 
    # Executing the ls -ltr command on the relevant connected server
    con_obj.exec_command(command='ls -ltr')
 