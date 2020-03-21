import http.server
import socketserver
from http import HTTPStatus
import json

from cube import Cube


PORT = 12345


def get_state(cube):
    state_dict = {"pieces": []}
    for piece in cube.pieces:
        piece_dict = {"position": tuple(piece.position),
                      "orientation": (piece.orientation.x,
                                      piece.orientation.y,
                                      piece.orientation.z,
                                      piece.orientation.w)}
        state_dict["pieces"].append(piece_dict)
    return state_dict


class CubeHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, request, client_address, server):
        super().__init__(request, client_address, server)

    def do_GET(self):
        if self.path == "/getstate":
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            state_json = get_state(global_cube)
            self.wfile.write(json.dumps(state_json).encode())
        else:  # fetch file normally
            super().do_GET()

    def do_POST(self):
        if self.path == "/maketurn":
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length).decode()
            data = json.loads(body)
            print("got data for maketurn", data)
            res = global_cube.rotate(data["move"])
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            state_json = get_state(global_cube)
            state_json["status"] = "ok" if res else "error"
            self.wfile.write(json.dumps(state_json).encode())
        else:
            print("Invalid post reqest to", self.path)


if __name__ == '__main__':
    global_cube = Cube(3)
    with socketserver.TCPServer(("", PORT), CubeHandler) as httpd:
        print("serving at port", PORT)
        httpd.serve_forever()
