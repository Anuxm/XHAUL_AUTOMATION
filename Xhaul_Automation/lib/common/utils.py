import os
import sys
import re
 
sys.path.insert(0,
                os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
ABSOLUTE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../'))
 
from lib.log.custom_log import Logger
 
LOG = Logger(__name__)
 
 
class Utils:
    """
    Utils is a class which carries the methods which are commonly used in most
    cases
    """
 
    def __init__(self) -> None:
        pass
 
    def get_process_id(self, process_name, con_obj):
        """
        get_process_id method is used to get the process id of the given
               input process name
        :param process_name: Name of the process to which the process ID has
           to be returned
        :type  process_name: Str
        :param: con_obj: Connection object
        :return: process_list
        """
        cli = f"ps -aux | grep {process_name}"
        output = con_obj.exec_command(cli)
        process_list = []
        pat = '[a-zA-Z]+\s+(\d+)\s+(.*)'
        for line in output.split("\n"):
            m0 = re.search(pat, line)
            if m0 and process_name in line:
                process_list.append(m0.group(1))
        if len(process_list) == 0:
            LOG.log_info(f"No Process named {process_name} is running..\
                unable to fetch process id")
        return process_list
 
    def kill_process(self, process_name, con_obj):
        """
        This kill_process will kill the running process in either host or soc
        :param process_name: Name of running process
        :type  process_name: Str
        :return: None
        """
        pid = self.get_process_id(process_name)
        for id in pid:
            con_obj.exec_command((f"kill -9 {id}"))
        pid_op = self.get_process_id(process_name)
        if len(pid_op) == 0:
            LOG.log_info("process id is killed successfully")
        else:
            raise RuntimeError("One or more process is not killed")
 
    def get_test_result(self, result: bool, tc_name: str) -> None:
        """
        This get_test_result method is used to provide the status for the
        testcase as fail/pass
        Args:
            result: This list carries True/False for all validations in our
             testcase
            tc_name: Name of the testcase
        Returns: None
        """
        result_flag = p_msg = f_msg = ""
        if not result:
            f_msg = f"Test FAILED : Test validation for the testcase \
                        {tc_name} Failed"
            result_flag = False
        else:
            p_msg = f"Test PASSED : Test validation for the testcase \
                        {tc_name} Passed "
            result_flag = True
        LOG.log_assert(result_flag, f_msg, p_msg)
 
 
if __name__ == "__main__":
    pass