import requests
from ArgParser import ArgParser
import json
import grpc
import service_file_pb2
import service_file_pb2_grpc

'''
Function write conntent of file to specified output
@param out_content is conntent to be writen
@param parametres is dictionary with default parametres
@misc append can be added
'''
def write_content_to_output(out_content, output):
    if output != '':
        with open(output, 'w', encoding='UTF8', newline='') as f:
            f.write(out_content)
    else:
        print(out_content)

'''
Function organize content of file and write to specified output
@param response is given response from rest
@param parametres is dictionary with default parametres
'''
def organize_out_content_rest(response, info_type):
    out_content = ''
    if(info_type == 'stat'):
        out_content = json.dumps(response.json(), indent=4)
    elif(info_type == 'read'):
        out_content = 'Content-Disposition ' + response.headers['Content-Disposition'] + '\n'
        out_content += 'Content-Type ' + response.headers['Content-Type'] + '\n'
        out_content += str(response.content.hex())
    return out_content

'''
Function organize content of file and write to specified output
@param response is given response from grpc
@param parametres is dictionary with default parametres
'''
def organize_out_content_stat_grpc(response):
    out_content = ''
    out_content = 'data {\n'
    out_content += '\tcreate_datetime: {\n'
    out_content += '\t\tseconds: ' + str(response.data.create_datetime.seconds) + '\n'
    out_content += '\t\tnanos: ' + str(response.data.create_datetime.nanos) + '\n'
    out_content += '\t}\n'
    out_content += '\tsize: ' + str(response.data.size) + '\n'
    out_content += '\tmimetype: "' + response.data.mimetype + '"\n'
    out_content += '\tname: "' + response.data.name + '"\n'
    out_content += '}'

    return out_content

'''
Function connecting to server and getting file using rest
@param parametres is dictionary with default parametres
@misc more/different reaction to another status codes may be added
'''
def rest_connection(parametres):
    try:
        response = requests.get(parametres['base-url'] + 'file/' + parametres['uuid'] + '/' + parametres['info_type'] + '/')
    except Exception as error:
        return 'Connection error.\n' + repr(error)
    if(response.status_code == 200):
        out_content = organize_out_content_rest(response, parametres['info_type'])
    elif(response.status_code == 404):
        out_content = 'File not found.'
    return out_content

'''
Function connecting to server and getting file using grcp
@param parametres is dictionary with default parametres
'''
def grpc_connection(parametres):
    reply = ''
    try:
        with grpc.insecure_channel(parametres['grpc-server']) as channel:
            stub = service_file_pb2_grpc.FileStub(channel)
            uu = service_file_pb2.Uuid(value = parametres['uuid'])
            if(parametres['info_type'] == 'stat'):
                request = service_file_pb2.StatRequest(uuid = uu)
                response= stub.stat(request)
                reply = organize_out_content_stat_grpc(response)
            elif(parametres['info_type'] == 'read'):
                request = service_file_pb2.ReadRequest(uuid = uu, size = parametres['size'])
                stream = stub.read(request)
                for read_reply in stream:
                    reply += str(read_reply.data.data.hex())
            return reply
    except Exception as error:
        return 'Connection error.\n' + repr(error)

'''
main function
'''
def main():
    parser = ArgParser()
    parser.parse_arguments()
    parametres = parser.dictionary
    
    if(parametres['help_flag'] == True):
        print(parser.help_message())
    elif(parametres['error_flag'] == True):
        print('Error with passed arguments. For correct use call with --help option.')
    else:
        if parametres['backend'] == 'rest':
            out_content = rest_connection(parametres)
            write_content_to_output(out_content, parametres['output'])
        elif parametres['backend'] == 'grpc':
            out_content = grpc_connection(parametres)
            write_content_to_output(out_content, parametres['output'])
        else:
            print('Wrong backend.')

if __name__ == '__main__':
    main()