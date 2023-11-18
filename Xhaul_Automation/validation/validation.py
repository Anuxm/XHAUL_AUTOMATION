
import os
import sys
 
sys.path.insert(0,
                os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
ABSOLUTE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../'))
 
from lib.log.custom_log import Logger
 
LOG = Logger(__name__)
 
 
class Validate:
    """
    Validate class is contains methods to validate given functionalities
    """
 
    def __init(self):
        pass
 
    def validate_page_load(self, attribute, element) -> bool:
        """
        This validate_page_load method is used to check weather particular
        page is loaded with required elements or not
        """
        # validation1
        if attribute:
            LOG.log_info(f"page is loaded without any issues with {element}")
            result = True
        else:
            LOG.log_error(f"Getting issues while loading page with {element}")
            result = False
        return result
 
    def validate_gui_test(self, error_msg: str) -> bool:
        """
        This validate_drop_down_gui_test method is used to validate
        drop down test
        :param : error_msg_list: list of all expected error massages
        :type : error_msg: str
        :return: True/False
        """
        expected_error_msg1 = ('Correct the highlighted errors and try again.',
                              'Please enter a value for this field.',
                              'Please enter a value for this field.',
                              'Please enter a value for this field.',
                              'Please enter a value for this field.',
                              'Please enter a value for this field.',
                              'Please enter a value for this field.',
                              'Please accept the terms of use before continuing.',
                              'Please verify you are not a robot.')
        expected_error_msg2 = ("The username or password is not recognized.")
        if all(i in error_msg for i in expected_error_msg1) or \
             error_msg in expected_error_msg2:
            LOG.log_info(f"test passed as expected:{error_msg}")
            result = True
        else:
            LOG.log_info(f'test Failed: {error_msg}')
            result = False
        return result
 
 
if __name__ == "__main__":
    pass