import unittest
from data.options import _parse_ini_file, _parse_args, get_config
import os
import sys
from StringIO import StringIO
import mock
from mock import patch

def get_file_path(filename):
    dir = os.path.dirname(__file__)
    return os.path.join(dir, filename)

GOOD_INI_FILEPATH = get_file_path('good_option_file.ini')
BAD_INI_FILEPATH = get_file_path('bad_option_file.ini')

class ServerStateTests(unittest.TestCase):
    def test_should_correctly_parse_good_ini_file(self):
        expectations = {'failure': False, 'successful_read': True, 
                        'server_configs': 
                        [{'host': '192.168.1.23', 'password': 'adminpass', 
                          'username': 'admin'}, 
                         {'host': '10.0.0.1', 'password': 'simverest', 
                         'username': 'simverest'}]
                       }
        result = _parse_ini_file(GOOD_INI_FILEPATH)
        self.assertEquals(expectations, result)

    def test_should_handle_badly_formatted_ini_file(self):
        expectations = {'failure': True, 'successful_read': False, 
                        'server_configs': []}
                        
        result = _parse_ini_file(BAD_INI_FILEPATH)
        self.assertEquals(expectations, result) 
        
    def test_should_handle_non_existent_formatted_ini_file(self):
        expectations = {'failure': False, 'successful_read': False, 
                        'server_configs': []}
                        
        ini_file_path = get_file_path('non_existent_file.ini')
        result = _parse_ini_file(ini_file_path)
        self.assertEquals(expectations, result)
        
    def test_should_have_default_arguments_if_no_config_specified(self):
        args = ['VRN1', 'admin', 'adminpass']
                     
        options = _parse_args(False, args)
        
        expectations = {'servers': [{'host': 'VRN1', 'username': 'admin', 
                        'password': 'adminpass'}], 'wsgi_server': 'wsgiref',
                        'port': 8080, 'stat_window': 5, 'test': False,
                        'config_file': ''}
        
        self.assertEquals(expectations, options)

    def test_should_have_default_executable_arguments_if_no_config_specified(self):
        test_args = ['VRN1', 'admin', 'adminpass']
                     
        options = _parse_args(True, test_args)
        
        expectations = {'servers': [{'host': 'VRN1', 'username': 'admin', 
                        'password': 'adminpass'}], 'wsgi_server': 'twisted',
                        'port': 8080, 'stat_window': 5, 'test': False,
                        'config_file': ''}
        
        self.assertEquals(expectations, options)
    
    def test_should_have_supplied_arguments_if_no_config_specified(self):
        test_args = ['VRN1', 'admin', 'adminpass', '-w', 'paste', '-p', 
                     '8091', '-s', '15']
                     
        options = _parse_args(False, test_args)
        
        
        expectations = {'servers': [{'host': 'VRN1', 'username': 'admin', 
                        'password': 'adminpass'}], 'wsgi_server': 'paste',
                        'port': 8091, 'stat_window': 15, 'test': False,
                        'config_file': ''}
        
        self.assertEquals(expectations, options)
        
    def test_should_have_supplied_executable_arguments_if_no_config_specified(self):
        args = ['VRN1', 'admin', 'adminpass', '-p', '8091', '-s', '15']
                     
        options = _parse_args(True, args)
        expectations = {'servers': [{'host': 'VRN1', 'username': 'admin', 
                        'password': 'adminpass'}], 'wsgi_server': 'twisted',
                        'port': 8091, 'stat_window': 15, 'test': False,
                        'config_file': ''}
        
        self.assertEquals(expectations, options)
        
    def test_should_handle_test_arguments(self):
        test_args = ['--test', '-w', 'gunicorn', '-p', '8091', '-s', '15']
                     
        options = _parse_args(False, test_args)
        
        expectations = {'wsgi_server': 'gunicorn', 'port': 8091, 
                        'stat_window': 15, 'test': True,
                        'config_file': ''}
        
        self.assertEquals(expectations, options)
        
    def test_should_not_have_required_arguments_if_config_specified(self):
        args = ['-c', 'dummy_file', '-p', '8091', '-s', '15', '-w', 'twisted']
                     
        options = _parse_args(False, args)
        expectations = {'wsgi_server': 'twisted', 'port': 8091, 
                        'stat_window': 15, 'test': False, 
                        'config_file': 'dummy_file'}
        
        self.assertEquals(expectations, options)
        
    def test_should_not_add_handle_test_and_executable_arguments(self):
        test_args = ['--test']
        
        old_stderr = sys.stderr
        sys.stderr = StringIO()
        try:
            options = _parse_args(True, test_args)
            self.fail('Should throw an error because --test is not allow with executable')
        except SystemExit:
            pass
        finally:
            sys.stderr = old_stderr
    
    @mock.patch('data.options._parse_args')
    def test_should_remove_config_file_parameter(self, _parse_args_mock):
        _parse_args_mock.return_value = {'config_file': ''}
        
        config = get_config()
        
        self.assertEquals({}, config)
        
    def test_should_load_file_if_config_file_present(self):
        with patch('data.options._parse_args') as args_mock:
            args_mock.return_value = {'config_file': 'dummy_file.ini'}
            with patch('data.options._parse_ini_file') as ini_mock:
                ini_mock.return_value = {'failure': False, 'successful_read': True, 
                                 'server_configs': [{'host': '192.168.1.23', 
                                 'password': 'adminpass', 'user': 'admin'}, 
                                 {'host': '10.0.0.1', 'password': 'simverest', 
                                  'user': 'simverest'}]
                                }
                config = get_config()
                
        
        expectations = {'servers': [
                        {'host': '192.168.1.23', 'password': 'adminpass', 
                         'user': 'admin'}, 
                        {'host': '10.0.0.1', 'password': 'simverest', 
                         'user': 'simverest'}]}
        
        
        self.assertEquals(expectations, config)
    
    def test_should_exit_if_config_file_not_successfully_read(self):
        with patch('data.options._parse_args') as args_mock:
            args_mock.return_value = {'config_file': 'dummy_file.ini'}
            with patch('data.options._parse_ini_file') as ini_mock:
                ini_mock.return_value = {'failure': False, 'successful_read': False, 
                                 'server_configs': []}

                old_stderr = sys.stderr
                sys.stderr = StringIO()
                try:
                    with self.assertRaises(SystemExit):
                        config = get_config()
                    
                    self.assertEquals("Could not read 'dummy_file.ini'\n", sys.stderr.getvalue())
                finally:
                    sys.stderr = old_stderr
                    
    def test_should_exit_if_cannot_parse_config_file(self):
        with patch('data.options._parse_args') as args_mock:
            args_mock.return_value = {'config_file': 'dummy_file.ini'}
            with patch('data.options._parse_ini_file') as ini_mock:
                ini_mock.return_value = {'failure': True, 'successful_read': False, 
                                 'server_configs': []}

                old_stderr = sys.stderr
                sys.stderr = StringIO()
                try:
                    with self.assertRaises(SystemExit):
                        config = get_config()
                    
                    self.assertEquals("Could not parse 'dummy_file.ini'\n", sys.stderr.getvalue())
                finally:
                    sys.stderr = old_stderr
                    
        