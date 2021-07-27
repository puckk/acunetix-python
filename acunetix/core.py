#!/usr/bin/env python3
import requests
import json
requests.packages.urllib3.disable_warnings()

from .axeception import AXException
from .constants import *

class Acunetix(object):
    def __init__(self, host=None, api=None, timeout=20):
        self.apikey = api
        self.host = str(
            "{}{}".format("https://" if "https://" not in host else "", host)
        )
        self.timeout = timeout
        self.headers = {
            "X-Auth": self.apikey,
            "content-type": "application/json",
            "User-Agent": "Acunetix",
        }
        self.authenticated = self.__is_connected()
        if not self.authenticated:
            raise AXException("AUTH_ERROR", "Wrong API Key !")

    def __json_return(self, data):
        try:
            return json.loads(data)
        except Exception as e:
            return {}
            raise AXException("JSON_PARSING_ERROR", f"Json Parsing has occured: {e}")

    def __send_request(self, method="get", endpoint="", data=None):
        request_call = getattr(requests, method)
        url = str("{}{}".format(self.host, endpoint if endpoint else "/"))
        try:
            request = request_call(
                url,
                headers=self.headers,
                timeout=self.timeout,
                data=json.dumps(data),
                verify=False,
            )
            if request.status_code == 403:
                raise AXException("HTTP_ERROR", f"HTTP ERROR OCCURED: {request.text}")
            return self.__json_return(request.text)
        except Exception as e:
            raise AXException("HTTP_ERROR", f"HTTP ERROR OCCURED: {e}")

    def __is_connected(self):
        return False if 'Unauthorized' in str(self.info()) else True

    def info(self):
        return self.__send_request(method="get", endpoint="/api/v1/info")

    def targets(self):
        return self.__send_request(
            method="get", endpoint=f"{API_TARGET}?pagination=50"
        )

    def add_target(self, target="", criticality="normal"):
        if criticality not in target_criticality_allowed:
            raise AXException("NOT_ALLOWED_CRITICYLITY_PROFILE", "Criticallity not found allowed values {}".format(str(list(target_criticality_allowed))))        
        target_address = (
            target if "http://" in target or "https://" in target else "http://{}".format(target)
        )
        data = {
            "address": str(target_address),
            "description": "Sent from Acunetix-Python",
            "criticality": target_criticality_list[criticality],
        }
        print(f"adding target {target_address} ")
        return self.__send_request(method="post", endpoint=API_TARGET, data=data)

    def delete_target(self, target_id):
        print(f"deleting {target_id}")
        try:
            return self.__send_request(
                method="delete", endpoint=f"{API_TARGET}/{target_id}"
            )
        except:
            pass

    def delete_all_targets(self):
        while True:
            targets = self.targets()
            if len(targets["targets"]):
                for target in targets["targets"]:
                    self.delete_target(target["target_id"])
            else:
                break

    def scans(self):
        return self.__send_request(method="get", endpoint=API_SCAN)

    def start_scan(self, address=None, target_id=None, scan_profile="full_scan"):
        if scan_profile not in scan_profiles_allowed:
            raise AXException("NOT_ALLOWED_SCAN_PROFILE", "Scan Profile not found allowed values {}".format(str(list(scan_profiles_allowed))))
        if address and not target_id:
            target_id = self.add_target(target=address)["target_id"]
        scan_payload = {
            "target_id": str(target_id),
            "profile_id": scan_profiles_list[scan_profile],
            "schedule": {"disable": False, "start_date": None, "time_sensitive": False},
        }
        print(f"Scanning {target_id} , {scan_profile}")
        return self.__send_request(method="post", endpoint=API_SCAN , data=scan_payload)

    def configure(self, target_id, scan_profile="full_scan", proxy_address="", proxy_port=""):

        configure_payload = {"scan_speed":"fast","login":{"kind":"none"},"ssh_credentials":{"kind":"none"},"default_scanning_profile_id":scan_profiles_list[scan_profile],"sensor":False,"case_sensitive":"no","limit_crawler_scope": False,"excluded_paths":[],"authentication":{"enabled":False},"proxy":{"enabled":True,"protocol":"http","address":proxy_address,"port":proxy_port},"technologies":[],"custom_headers":[],"custom_cookies":[],"debug":False,"restrict_scans_to_import_files":False,"client_certificate_password":"","user_agent":"","client_certificate_url":"","issue_tracker_id":"","excluded_hours_id":"","preseed_mode":""}
        return self.__send_request(method="patch", endpoint=API_CONFIGURE_TARGET.format(target_id), data=configure_payload)
