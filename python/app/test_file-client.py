import unittest
import importlib
import threading
import re
from grpc_server import run_server
from ArgParser import ArgParser
import time
import sys
import io
import os

#testing class
class TestClient(unittest.TestCase):

    #before tests
    @classmethod
    def setUpClass(cls):
        cls.file_client = importlib.import_module('file-client')
        cls.grpc_server_thread = threading.Thread(target=run_server, name='Server', args=[5]) #runs for five secconds, that should be enought to run tests
        cls.grpc_server_thread.start()
        time.sleep(0.1) #wait for server to start
        
        cls.parser = ArgParser()
        cls.test_file = 'test_file.txt'
        cls.file_name = os.path.join(os.path.dirname(__file__), cls.test_file)

    #after tests
    @classmethod
    def tearDownClass(cls):
        os.remove(cls.file_name)

    #stats of grpc
    def grpc_stat(self, seconds, nanos, size, mime, name):
        out_content = 'data {\n'
        out_content += '\tcreate_datetime: {\n'
        out_content += '\t\tseconds: ' + seconds + '\n'
        out_content += '\t\tnanos: ' + nanos + '\n'
        out_content += '\t}\n'
        out_content += '\tsize: ' + size + '\n'
        out_content += '\tmimetype: "' + mime + '"\n'
        out_content += '\tname: "' + name + '"\n'
        out_content += '}'
        return out_content

    #stats of rest
    def rest_stat(self, datetime, mime, name, size):
        out_content = '{\n'
        out_content += '    \"stats\": [\n'
        out_content += '        {\n'
        out_content += '            \"create_datetime\": \"' + datetime + '\",\n'
        out_content += '            \"mimetype\": \"' + mime + '\",\n'
        out_content += '            \"name\": \"' + name + '\",\n'
        out_content += '            \"size\": ' + size + '\n'
        out_content += '        }\n'
        out_content += '    ]\n'
        out_content += '}'
        return out_content

    #testing grpc
    def test_grpc_connection(self):
        #correct parametres and target (reading small content size of 7, localhost)
        parametres = {'grpc-server' : 'localhost:50051', 'uuid' : '9c465aa7-05fd-46eb-b759-344c48abc85f', 'info_type' : 'stat', 'output' : '', 'size' : 3}
        self.assertEqual(self.file_client.grpc_connection(parametres), self.grpc_stat('1656633600', '0', '7', 'txt', 'asd'))
        parametres['info_type'] = 'read'
        self.assertEqual(self.file_client.grpc_connection(parametres), "content")

        #wrong uuid
        parametres['uuid'] = 'asd'
        self.assertEqual(self.file_client.grpc_connection(parametres), '')
        parametres['info_type'] = 'stat'
        self.assertEqual(self.file_client.grpc_connection(parametres), self.grpc_stat('0', '0', '0', '', ''))

        #wrong address
        parametres['grpc-server'] = 'localhost:50038'
        self.assertRegex(self.file_client.grpc_connection(parametres), r'^Connection error.\n')
        parametres['info_type'] = 'read'
        self.assertRegex(self.file_client.grpc_connection(parametres), r'^Connection error.\n')

    #testing rest (server must be run before test starts)
    def test_rest_connection(self):
        #correct parametres and target (localhost)
        parametres = {'base-url' : 'http://127.0.0.1:5000/', 'uuid' : '9c465aa7-05fd-46eb-b759-344c48abc85f', 'info_type' : 'stat', 'output' : '', 'size' : 3}
        self.assertEqual(self.file_client.rest_connection(parametres), self.rest_stat('2021-02-14 11:22:33.000', 'image', 'asd', '5'))
        parametres['info_type'] = 'read'
        self.assertEqual(self.file_client.rest_connection(parametres), 'Content-Disposition inline; filename=test.txt\nContent-Type text/plain; charset=utf-8\n')

        #wrong uuid
        parametres['uuid'] = 'asd'
        self.assertEqual(self.file_client.rest_connection(parametres), 'File not found.')
        parametres['info_type'] = 'stat'
        self.assertEqual(self.file_client.rest_connection(parametres), 'File not found.')

        #wrong address
        parametres['base-url'] = 'localhost:50038'
        self.assertRegex(self.file_client.rest_connection(parametres), r'^Connection error.\n')
        parametres['info_type'] = 'read'
        self.assertRegex(self.file_client.rest_connection(parametres), r'^Connection error.\n')

    #testing writing to output
    def test_write_content_to_output(self):
        #test stdout
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        self.file_client.write_content_to_output('out_content', '')
        self.assertEqual(capturedOutput.getvalue(), 'out_content\n')
        sys.stdout = sys.__stdout__

        #test write to file
        self.file_client.write_content_to_output('out_content', self.test_file)
        testfile = open(self.file_name)
        testdata = testfile.read()
        self.assertEqual(testdata, 'out_content')
        testfile.close()

    #testing module AgrParser (maybe it would be ideal separate it into multiple tests for unit testing)
    def test_ArgParser(self):
        #--help
        self.parser.parse_arguments(['file-client', '--elp'])
        self.assertEqual(self.parser.parametres['help_flag'], False)

        self.parser.parse_arguments(['file-client', '--help', 'base-url=123'])
        self.assertEqual(self.parser.parametres['help_flag'], False)

        self.parser.parse_arguments(['file-client', '--help'])
        self.assertEqual(self.parser.parametres['help_flag'], True)

        #set_options
        self.parser.set_to_default()

        self.parser.set_options(['file-client', '--base-url=http://127.0.0.1:5000/', '--backend=rest', 'read', '9c465aa7-05fd-46eb-b759-344c48abc85f'])
        self.assertEqual(self.parser.parametres['error_flag'], False)
        self.assertEqual(self.parser.parametres['base-url'], 'http://127.0.0.1:5000/')
        self.assertEqual(self.parser.parametres['backend'], 'rest')

        self.parser.set_options(['file-client']) #no options
        self.assertEqual(self.parser.parametres['error_flag'], False) #subcommands and amount are not checked here

        self.parser.set_options(['file-client', 'read', '9c465aa7-05fd-46eb-b759-344c48abc85f']) #no options
        self.assertEqual(self.parser.parametres['error_flag'], False)

        self.parser.set_options(['file-client', '--base-url=http://127.0.0.1:5000/', '--base-url=http://127.0.0.1:5000/'])
        self.assertEqual(self.parser.parametres['error_flag'], True)

        #set_subcommand
        self.parser.set_to_default()
        self.parser.set_subcommands(['file-client', 'read', '9c465aa7-05fd-46eb-b759-344c48abc85f'])
        self.assertEqual(self.parser.parametres['error_flag'], False)
        self.assertEqual(self.parser.parametres['info_type'], 'read')
        self.assertEqual(self.parser.parametres['uuid'], '9c465aa7-05fd-46eb-b759-344c48abc85f')

        self.parser.set_to_default() #subcommands passed in opposite order also works (it could be wrong, i think its fine)
        self.parser.set_subcommands(['file-client', '9c465aa7-05fd-46eb-b759-344c48abc85f', 'stat'])
        self.assertEqual(self.parser.parametres['error_flag'], False)
        self.assertEqual(self.parser.parametres['info_type'], 'stat')
        self.assertEqual(self.parser.parametres['uuid'], '9c465aa7-05fd-46eb-b759-344c48abc85f')

        self.parser.set_to_default() #wrong number of subcommands (after options are removed)
        self.parser.set_subcommands(['file-client', 'asd', '9c465aa7-05fd-46eb-b759-344c48abc85f', 'stat'])
        self.assertEqual(self.parser.parametres['error_flag'], True)

        self.parser.set_to_default() #no subcommands (after options are removed)
        self.parser.set_subcommands(['file-client'])
        self.assertEqual(self.parser.parametres['error_flag'], True)

        #parse_arguments
        self.parser.set_to_default()
        self.parser.parse_arguments(['file-client', '--base-url=http://127.0.0.1:5000/', '--backend=rest', 'stat', '9c465aa7']) #correct
        self.assertEqual(self.parser.parametres['error_flag'], False)
        self.assertEqual(self.parser.parametres['help_flag'], False)
        self.assertEqual(self.parser.parametres['base-url'], 'http://127.0.0.1:5000/')
        self.assertEqual(self.parser.parametres['backend'], 'rest')
        self.assertEqual(self.parser.parametres['info_type'], 'stat')
        self.assertEqual(self.parser.parametres['uuid'], '9c465aa7')

        self.parser.set_to_default()
        self.parser.parse_arguments(['file-client', '9c465aa7'])
        self.assertEqual(self.parser.parametres['error_flag'], True)
        self.assertEqual(self.parser.parametres['help_flag'], False)

        self.parser.set_to_default()
        self.parser.parse_arguments(['file-client', 'read'])
        self.assertEqual(self.parser.parametres['error_flag'], True)
        self.assertEqual(self.parser.parametres['help_flag'], False)

        self.parser.set_to_default()
        self.parser.parse_arguments(['file-client', 'stat', '9c465aa7'])
        self.assertEqual(self.parser.parametres['error_flag'], False)
        self.assertEqual(self.parser.parametres['help_flag'], False)

        self.parser.set_to_default()
        self.parser.parse_arguments(['file-client', '--help', 'stat', '9c465aa7'])
        self.assertEqual(self.parser.parametres['error_flag'], True)
        self.assertEqual(self.parser.parametres['help_flag'], False)

        self.parser.set_to_default()
        self.parser.parse_arguments(['file-client', 'url=http://127.0.0.1:5000/', 'stat', '9c465aa7'])
        self.assertEqual(self.parser.parametres['error_flag'], True)
        self.assertEqual(self.parser.parametres['help_flag'], False)

        self.parser.set_to_default()
        self.parser.parse_arguments(['file-client', '--help'])
        self.assertEqual(self.parser.parametres['error_flag'], False)
        self.assertEqual(self.parser.parametres['help_flag'], True)

if __name__ == '__main__':
    unittest.main()