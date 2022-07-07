#!/usr/bin/env python3

import requests

HOST = "http://localhost:8123"

res = requests.get(HOST + "/?give=flag")

assert res.status_code == 200, "Webserver is not responding correctly"
assert "CTF" in res.text

print("Got flag: {}".format(res.text))