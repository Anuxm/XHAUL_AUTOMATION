import logging
import os
import pathlib
 
from time import strftime
from configparser import ConfigParser
 
 
class Logger:
    """
    Logger class is a wrapper around logging module to have a generic
    logging retrieving log parameters from pytest.ini file.
    A File handler is created with methods to provision logging of info, debug
    error, warning and assert. A Header method is also provided to print
    Multiline Log for testcases
    :parameter module_name: name of the module from which
    this class has been initiated
    :type module_name: str
    """
 
    def __init__(self, module_name):
        parser = ConfigParser()
        log_cli_level = "INFO"
        log_file = "xhaul_test"
        cwd = os.getcwd()
        output_dir = "{0}/output".format(cwd)
        logging.setLoggerClass(CustomLogger)
        self.logger_module = logging.getLogger(module_name)
        self.logger_module.setLevel(log_cli_level)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        filehandler = logging.FileHandler(
            pathlib.Path(output_dir, strftime("{0}_%H_%M_%m_%d_%Y.log").format(log_file)))
        filehandler.setLevel(log_cli_level)
        fileformatter = logging.Formatter(
            "%(asctime)s - %(name)s.py  : %(lineno)d -"
            " %(levelname)s -  %(message)s")
        filehandler.setFormatter(fileformatter)
        self.logger_module.addHandler(filehandler)
        logging.setLoggerClass(logging.Logger)
 
    def log_info(self, message, *args, **kwargs):
        """Method to Log with info Level
        :parameter message : Custom message to be logged in as info
        :type message : string
        """
        self.logger_module.info(message, *args, **kwargs)
 
    def log_error(self, message, *args, **kwargs):
        """Method to Log with Error Level
        :parameter message : Custom message to be logged in as info
        :type message : str
        """
        self.logger_module.error(message, *args, **kwargs)
 
    def log_debug(self, message, *args, **kwargs):
        """Method to Log with debug Level
        :parameter message : Custom message to be logged in as info
        :type message : str
        """
        self.logger_module.debug(message, *args, **kwargs)
 
    def log_title(self, message, *args, **kwargs):
        """Method to Log title in a format with info Level
        :parameter message : Custom message to be logged in as Title
        :type message : str
        """
        str = "*" * len(message)
        message = "\n {0} \n {1} \n {0}".format(str, message)
        self.log_info((message.center(len(message) + 20)))
 
    def log_assert(self, test, msg1, msg2):
        """Method to assert the testcases
        :parametermessage : Custom message to be logged in as Header
        :typemessage : str
        """
 
        if not test:
            str = "%" * len(msg1)
            msg1 = f"\n {str} \n FAIL: {msg1} \n {str}"
            self.log_error(msg1)
            assert test, msg1
        else:
            str = "#" * len(msg2)
            msg2 = f"\n {str} \n PASS: {msg2} \n {str}"
            self.log_info(msg2)
 
 
class CustomLogger(logging.Logger):
    """Class CustomLogger is wrapper around logging module to
    have a generic logging Here we create file handler which logs even
    debug messages, create formatter and add it to the handlers and
    define different log levels"""
 
    @staticmethod
    def findCaller(stack_info=False, stacklevel=1):
        """
        Find the stack frame of the caller so that we can note the correct
        file name, line number and function name.
        :parameter: stack_info: stack_info defaults to 0
        :type:stack_info: bool
        :param: stacklevel: It defaults to 1
        :type:stacklevel: int
        :return: r_v: returns lineno filename as a tuple
        """
        n_frames_upper = 2
        frame = logging.currentframe()
        for _ in range(n_frames_upper):
            if frame is not None:
                frame = frame.f_back
        r_v = "(unknown file)", 0, "(unknown function)", None
        while hasattr(frame, "f_code"):
            c_o = frame.f_code
            filename = os.path.normcase(c_o.co_filename)
            if filename == logging._srcfile:
                frame = frame.f_back
                continue
            r_v = (c_o.co_filename, frame.f_lineno, c_o.co_name, None)
            break
        return r_v
 
 
if __name__ == "__main__":
    Logger = Logger("ModuleName")
    Logger.log_debug("Debug")
    Logger.log_info("Info")
 
 
