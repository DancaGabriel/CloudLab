import http.server
import json
import xml.etree.ElementTree as ET
import os
from xml.dom import minidom

PORT = 9999
fisier = "data.xml"

class Clasa(http.server.BaseHTTPRequestHandler):
    def _set_headers(self, status=200, content_type="application/json"):
        self.send_response(status)
        self.send_header("Content-type", content_type)
        self.end_headers()

    def do_GET(self):
        if self.path.startswith("/resource"):
            parts = self.path.strip("/").split("/")
            data = self.read_data()
            if len(parts) == 1:
                self._set_headers()
                self.wfile.write(json.dumps(data).encode())
            elif len(parts) == 2:
                resource_id = parts[1]
                resource = next((r for r in data if r.get("id") == resource_id), None)
                if resource:
                    self._set_headers()
                    self.wfile.write(json.dumps(resource).encode())
                else:
                    self._set_headers(404)
                    self.wfile.write(json.dumps({"error": "Resource not found"}).encode())
            else:
                self._set_headers(404)
                self.wfile.write(json.dumps({"error": "Not Found"}).encode())
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Not Found"}).encode())

    def do_POST(self): # create
        if self.path == "/resource":
            content_length = int(self.headers.get("Content-Length", 0))
            post_data = self.rfile.read(content_length)
            try:
                resource = json.loads(post_data)
                data = self.read_data()
                new_id = str(len(data) + 1)
                resource["id"] = new_id
                data.append(resource)
                self.write_data(data)
                self._set_headers(201)
                self.wfile.write(json.dumps(resource).encode())
            except Exception as e:
                self._set_headers(500)
                self.wfile.write(json.dumps({"error": str(e)}).encode())
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Not Found"}).encode())

    def do_PUT(self): # update
        if self.path.startswith("/resource/"):
            parts = self.path.strip("/").split("/")
            if len(parts) == 2:
                resource_id = parts[1]
                content_length = int(self.headers.get("Content-Length", 0))
                put_data = self.rfile.read(content_length)
                try:
                    updated_resource = json.loads(put_data)
                    data = self.read_data()
                    resource_found = False
                    for idx, r in enumerate(data):
                        if r.get("id") == resource_id:
                            updated_resource["id"] = resource_id
                            data[idx] = updated_resource
                            resource_found = True
                            break
                    if resource_found:
                        self.write_data(data)
                        self._set_headers(200)
                        self.wfile.write(json.dumps(updated_resource).encode())
                    else:
                        self._set_headers(404)
                        self.wfile.write(json.dumps({"error": "Resource not found"}).encode())
                except Exception as e:
                    self._set_headers(500)
                    self.wfile.write(json.dumps({"error": str(e)}).encode())
            else:
                self._set_headers(404)
                self.wfile.write(json.dumps({"error": "Not Found"}).encode())
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Not Found"}).encode())

    def do_DELETE(self):
        if self.path.startswith("/resource/"):
            parts = self.path.strip("/").split("/")
            if len(parts) == 2:
                resource_id = parts[1]
                data = self.read_data()
                new_data = [r for r in data if r.get("id") != resource_id]
                if len(new_data) != len(data):
                    self.write_data(new_data)
                    self._set_headers(200)
                    self.wfile.write(json.dumps({"message": "Resource deleted"}).encode())
                else:
                    self._set_headers(404)
                    self.wfile.write(json.dumps({"error": "Resource not found"}).encode())
            else:
                self._set_headers(404)
                self.wfile.write(json.dumps({"error": "Not Found"}).encode())
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Not Found"}).encode())

    def read_data(self):
        if not os.path.exists(fisier):
            root = ET.Element("resources")
            tree = ET.ElementTree(root)
            tree.write(fisier, encoding="utf-8")
            return []
        try:
            tree = ET.parse(fisier)
            root = tree.getroot()
            return [{child.tag: child.text for child in res} for res in root.findall("resource")]
        except Exception as e:
            print("Error reading data:", e)
            return []

    def write_data(self, data):
        root = ET.Element("resources")
        for resource in data:
            res_elem = ET.SubElement(root, "resource")
            for key, value in resource.items():
                child = ET.SubElement(res_elem, key)
                child.text = str(value)
        xml_str = ET.tostring(root, encoding="utf-8", method="xml")
        parsed_xml = minidom.parseString(xml_str)
        pretty_xml = "\n".join([line for line in parsed_xml.toprettyxml(indent="    ").split("\n") if line.strip()])
        with open(fisier, "w", encoding="utf-8") as f:
            f.write(pretty_xml)

def main():
    server_address = ('', PORT)
    httpd = http.server.HTTPServer(server_address, Clasa)
    print(f"Server running at http://localhost:{PORT}/")
    httpd.serve_forever()

if __name__ == "__main__":
    main()
