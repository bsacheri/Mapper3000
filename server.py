#!/usr/bin/env python3
"""
Static file server for garage-sale-map.html, plus same-origin proxies for the
US Census geocoder, openrouteservice, and MapQuest. Those services can reject
browser cross-origin requests, while requests forwarded by this local server
are not subject to the browser's CORS policy.
"""
import http.server
import json
import urllib.request
import urllib.parse

CENSUS_URL = "https://geocoding.geo.census.gov/geocoder/locations/onelineaddress"
ORS_BASE_URL = "https://api.openrouteservice.org/v2"
ORS_PROFILES = {
    "cycling-regular", "cycling-electric", "cycling-road", "cycling-mountain",
    "foot-walking", "driving-car",
}
MAPQUEST_BASE_URL = "https://www.mapquestapi.com/directions/v2"
MAPQUEST_ROUTE_TYPES = {"bicycle", "pedestrian", "fastest", "shortest"}

class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/api/census":
            qs = urllib.parse.parse_qs(parsed.query)
            address = qs.get("address", [""])[0]
            if not address:
                self.send_error(400, "missing address param")
                return
            url = CENSUS_URL + "?" + urllib.parse.urlencode({
                "benchmark": "Public_AR_Current",
                "format": "json",
                "address": address,
            })
            try:
                with urllib.request.urlopen(url, timeout=10) as resp:
                    body = resp.read()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
            except Exception as e:
                self.send_response(502)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode())
            return
        return super().do_GET()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path_parts = parsed.path.strip("/").split("/")

        if len(path_parts) == 4 and path_parts[:2] == ["api", "ors"]:
            self._proxy_ors(path_parts[2], path_parts[3])
            return
        if len(path_parts) == 3 and path_parts[:2] == ["api", "mapquest"]:
            self._proxy_mapquest(path_parts[2], parsed.query)
            return
        self.send_error(404, "not found")

    def _read_body(self):
        content_length = int(self.headers.get("Content-Length", "0"))
        return self.rfile.read(content_length)

    def _forward(self, request):
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                return response.read(), response.status, response.headers.get("Content-Type", "application/json")
        except urllib.error.HTTPError as error:
            return error.read(), error.code, error.headers.get("Content-Type", "application/json")
        except Exception as error:
            return json.dumps({"error": str(error)}).encode(), 502, "application/json"

    def _respond(self, body, status, content_type):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _proxy_ors(self, service, profile):
        if service not in {"matrix", "directions"} or profile not in ORS_PROFILES:
            self.send_error(400, "unsupported ORS service or profile")
            return
        request_body = self._read_body()
        headers = {"Content-Type": "application/json", "Accept": "application/json, application/geo+json"}
        authorization = self.headers.get("Authorization")
        if authorization:
            headers["Authorization"] = authorization
        request = urllib.request.Request(
            f"{ORS_BASE_URL}/{service}/{profile}" + ("/geojson" if service == "directions" else ""),
            data=request_body,
            headers=headers,
            method="POST",
        )
        body, status, content_type = self._forward(request)
        self._respond(body, status, content_type)

    def _proxy_mapquest(self, service, query):
        # MapQuest takes its API key as a query parameter rather than a
        # header, so the browser sends `?key=...` straight through here and
        # this just re-attaches it to the real MapQuest URL.
        if service not in {"routematrix", "route"}:
            self.send_error(400, "unsupported MapQuest service")
            return
        qs = urllib.parse.parse_qs(query)
        key = qs.get("key", [""])[0]
        if not key:
            self.send_error(400, "missing key param")
            return
        request_body = self._read_body()
        url = f"{MAPQUEST_BASE_URL}/{service}?" + urllib.parse.urlencode({"key": key})
        request = urllib.request.Request(
            url,
            data=request_body,
            headers={"Content-Type": "application/json", "Accept": "application/json"},
            method="POST",
        )
        body, status, content_type = self._forward(request)
        self._respond(body, status, content_type)

if __name__ == "__main__":
    port = 8000
    # ThreadingHTTPServer, not plain HTTPServer: a proxied request can block
    # for several seconds (or the full 30s timeout) waiting on ORS/MapQuest.
    # A single-threaded server can't serve anything else -- not even the main
    # page -- while that one request is in flight.
    server = http.server.ThreadingHTTPServer(("", port), Handler)
    print(f"Serving on http://localhost:{port} (with Census, ORS, and MapQuest proxies)")
    server.serve_forever()
