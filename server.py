import http.server
import socketserver
from http import HTTPStatus
import json

from cube import Cube


PORT = 12345


class CubeHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, request, client_address, server):
        self.cube = Cube(3)
        for i in range(3):
            self.cube.rotate("R")
            self.cube.rotate("U")
            self.cube.rotate("R'")
            self.cube.rotate("U'")
        super().__init__(request, client_address, server)

    def get_state(self):
        state_dict = {"pieces": []}
        for piece in self.cube.pieces:
            piece_dict = {"position": tuple(piece.position),
                          "orientation": (piece.orientation.x,
                                          piece.orientation.y,
                                          piece.orientation.z,
                                          piece.orientation.w)}
            state_dict["pieces"].append(piece_dict)
        return json.dumps(state_dict)

    def do_GET(self):
        if self.path == "/getstate":
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-type", "application/json")
            state_json = self.get_state()
            self.send_header("Content-Length", str(len(state_json)))
            self.end_headers()
            self.wfile.write(state_json.encode())
        else:  # fetch file normally
            super().do_GET()


if __name__ == '__main__':
    with socketserver.TCPServer(("", PORT), CubeHandler) as httpd:
        print("serving at port", PORT)
        httpd.serve_forever()
