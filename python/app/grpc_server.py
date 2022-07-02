from concurrent import futures
import grpc
import service_file_pb2
import service_file_pb2_grpc
from google.protobuf.timestamp_pb2 import Timestamp
import datetime

class FileServicer(service_file_pb2_grpc.FileServicer):
    def stat(self, request, context):
        now = datetime.datetime(2022, 7, 1) 
        timestamp = Timestamp()
        timestamp.FromDatetime(now)

        if request.uuid.value != "9c465aa7-05fd-46eb-b759-344c48abc85f":
            reply = service_file_pb2.StatReply(data = service_file_pb2.StatReply.Data(create_datetime = None, size = None, mimetype = None, name = None))
        else:
            reply = service_file_pb2.StatReply(data = service_file_pb2.StatReply.Data(create_datetime = timestamp, size = 7, mimetype = "txt", name = "asd"))
        return reply

    def read(self, request, context):
        content = bytes.fromhex('636f6e74656e74')

        prew_i = 0
        i = request.size
        all_send = False
        if request.uuid.value != "9c465aa7-05fd-46eb-b759-344c48abc85f":
            reply = service_file_pb2.ReadReply(data = service_file_pb2.ReadReply.Data(data = None))
            yield reply
        else:
            while True:
                if i > len(content):
                    i = len(content)
                    all_send = True
                reply = service_file_pb2.ReadReply(data = service_file_pb2.ReadReply.Data(data = content[prew_i:i]))
                prew_i = i
                i += request.size
                yield reply
                if all_send:
                    break

def run_server(timeout):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    service_file_pb2_grpc.add_FileServicer_to_server(FileServicer(), server)
    server.add_insecure_port("localhost:50051")
    server.start()
    if(timeout != 0):
        server.wait_for_termination(timeout)
    else:
        server.wait_for_termination()

if __name__ == "__main__":
    run_server(0)