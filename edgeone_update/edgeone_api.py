#!/usr/bin/env python3
# -*- coding:utf-8 -*-

__author__ = "Guation"
__all__ = ["update_record", "init"]

import time, hashlib, hmac, requests, json
from logging import debug, info, warning, error

__id: str = None
__token: str = None
__sub_domain: str = None
__domain: str = None

def init(id: str, token: str, sub_domain: str, domain: str):
    global __id, __token, __sub_domain, __domain
    __id = id
    __token = token
    __sub_domain = sub_domain
    __domain = domain

def hmac_sha256(key: bytes, data: str) -> bytes:
    return hmac.new(key, data.encode("utf-8"), hashlib.sha256).digest()

def request(action: str, params: dict = None):
    timestamp = int(time.time())
    date = time.strftime('%Y-%m-%d', time.gmtime(timestamp))
    headers = {
        "content-type": "application/json",
        "host": "teo.tencentcloudapi.com",
        "x-tc-action": action,
        "x-tc-version": "2022-09-01",
        "x-tc-timestamp": str(timestamp)
    }
    headers = dict(sorted(headers.items()))
    canonical_headers = "\n".join(f"{k}:{v.lower()}" for k, v in headers.items()) + "\n"
    signed_headers = ";".join(headers.keys())
    params_string = json.dumps(params)
    canonical_request = "\n".join(["POST", "/", "", canonical_headers, signed_headers, hashlib.sha256(params_string.encode("utf-8")).hexdigest()])
    hashed_canonical_request = hashlib.sha256(canonical_request.encode("utf-8")).hexdigest()
    secretSigning = hmac_sha256(hmac_sha256(hmac_sha256(b"TC3" + __token.encode("utf-8"), date), "teo"), "tc3_request")
    credentialScope = f"{date}/teo/tc3_request"
    signature = hmac_sha256(secretSigning, f"TC3-HMAC-SHA256\n{timestamp}\n{credentialScope}\n{hashed_canonical_request}").hex().lower()
    headers["Authorization"] = f"TC3-HMAC-SHA256 Credential={__id}/{credentialScope}, SignedHeaders={signed_headers}, Signature={signature}"
    debug("action=%s, params=%s, headers=%s", action, params, headers)
    try:
        response = requests.request("POST", f"https://{headers['host']}/", headers=headers, data=params_string)
        r = response.content
        if response.status_code != 200:
            raise ValueError(
                '服务器拒绝了请求：action=%s, status_code=%d, response=%s' % (action, response.status_code, r)
            )
        else:
            j = json.loads(r)["Response"]
            if "Error" in j:
                raise ValueError(
                    '服务器返回错误：action=%s, response=%s' % (action, j)
                )
            else:
                debug("action=%s, response=%s", action, j)
                return j
    except ValueError:
        raise
    except Exception as e:
        raise ValueError(
            "%s 请求失败" % action
        ) from e

def search_zoneid(domain: str) -> str:
    for i in request("DescribeZones", {})["Zones"]:
        if domain == i["ZoneName"]:
            return i["ZoneId"]
    raise ValueError(
        "无法搜索到域名%s" % domain
    )

def search_recordid(sub_domain: str, zoneid: str) -> str:
    params = {
        "ZoneId": zoneid,
        "Limit": 200
    }
    for i in request("DescribeAccelerationDomains", params)["AccelerationDomains"]:
        if sub_domain == i["DomainName"]:
            return i["DomainName"]
    raise ValueError(
        "无法搜索到前缀%s" % sub_domain
    )

def update_record(ip: str, port: int):
    sub_domain = __sub_domain
    domain = __domain
    zoneid = search_zoneid(domain)
    recordid = search_recordid(f"{sub_domain}.{domain}", zoneid)
    payload = {
        "ZoneId": zoneid,
        "DomainName": recordid,
        "OriginInfo": {
            "OriginType": "IP_DOMAIN",
            "Origin": ip
        },
        "HttpOriginPort": port,
        "HttpsOriginPort": port,
    }
    return request("ModifyAccelerationDomain", payload)
