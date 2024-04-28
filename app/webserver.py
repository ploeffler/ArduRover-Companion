import http.server
import socketserver
import threading

PORT = 8001
DIRECTORY = "webclient"


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)



def create_server():
    my_server = socketserver.TCPServer(("", PORT), Handler)
    print("Webserver running at port:" + str(PORT))
    my_server.serve_forever()


websthread = threading.Thread(target=create_server)
