import unittest
import importlib
import threading
import re
from grpc_server import run_server
import time

#testing class
class TestClient(unittest.TestCase):

    #before tests
    def setUp(self):
        self.file_client = importlib.import_module('file-client')
        self.grpc_server_thread = threading.Thread(target=run_server, name='Server', args=[5]) #runs for ten seccond, but that should be enought to run tests
        self.grpc_server_thread.start()
        time.sleep(0.2) #wait for server to start

    #after tests
    def tearDown(self):
        pass

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
        #correct parametres and target (reading small content size of 7)
        parametres = {'grpc-server' : 'localhost:50051', 'uuid' : '9c465aa7-05fd-46eb-b759-344c48abc85f', 'info_type' : 'stat', 'output' : '', 'size' : 3}
        self.assertEqual(self.file_client.grpc_connection(parametres), self.grpc_stat('1656633600', '0', '7', 'txt', 'asd'))
        parametres['info_type'] = 'read'
        self.assertEqual(self.file_client.grpc_connection(parametres), '636f6e74656e74')

        #wrong uuid
        parametres['uuid'] = 'asd'
        self.assertEqual(self.file_client.grpc_connection(parametres), '')
        parametres['info_type'] = 'stat'
        self.assertEqual(self.file_client.grpc_connection(parametres), self.grpc_stat('0', '0', '0', '', ''))

        #wrong adress
        parametres['grpc-server'] = 'localhost:50038'
        self.assertRegex(self.file_client.grpc_connection(parametres), r'^Connection error.\n')
        parametres['info_type'] = 'read'
        self.assertRegex(self.file_client.grpc_connection(parametres), r'^Connection error.\n')

    #testing rest (server must be run before test starts)
    def test_rest_connection(self):
        #correct parametres and target (reading small content size of 7)
        parametres = {'base-url' : 'http://127.0.0.1:5000/', 'uuid' : '9c465aa7-05fd-46eb-b759-344c48abc85f', 'info_type' : 'stat', 'output' : '', 'size' : 3}
        self.assertEqual(self.file_client.rest_connection(parametres), self.rest_stat('2021-02-14 11:22:33.000', 'image', 'asd', '5'))
        parametres['info_type'] = 'read'
        self.assertEqual(self.file_client.rest_connection(parametres), 'Content-Disposition inline; filename=test.txt\nContent-Type text/plain; charset=utf-8\n')

        #wrong uuid
        parametres['uuid'] = 'asd'
        self.assertEqual(self.file_client.rest_connection(parametres), 'File not found.')
        parametres['info_type'] = 'stat'
        self.assertEqual(self.file_client.rest_connection(parametres), 'File not found.')

        #wrong adress
        parametres['base-url'] = 'localhost:50038'
        self.assertRegex(self.file_client.rest_connection(parametres), r'^Connection error.\n')
        parametres['info_type'] = 'read'
        self.assertRegex(self.file_client.rest_connection(parametres), r'^Connection error.\n')

    #testing writing to output
    def test_write_content_to_output(self):
        pass

    #testing module AgrParser
    def test_ArgParser(self):
        pass

if __name__ == '__main__':
    unittest.main()