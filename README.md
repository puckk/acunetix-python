# Acunetix Python API
```python

from acunetix import Acunetix

acunetix = Acunetix(host="serverip:port", api="xxxxxxxxxxxxxxxxxxxxxxxxxx")
scan_profile = "crawl_only"
proxy_address = "127.0.0.1"
proxy_port = 8080

domains = ['google.com','facebook.com','github.com']
for address in domains:
  target = acunetix.add_target(address)["target_id"]
  # Set proxy
  acunetix.configure(target, scan_profile=scan_profile, proxy_address=proxy_address, proxy_port=proxy_port)
  acunetix.start_scan(address=address, target_id=target, scan_profile="full_scan")
```
