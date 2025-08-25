#!/usr/bin/env python3
# -*- coding:utf-8 -*-

__author__ = "Guation"
__all__ = ["update_record", "init"]

from tencentcloud.common.common_client import CommonClient
from tencentcloud.common import credential
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
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

def request(action: str, params: dict = None):
    cred = credential.Credential(__id, __token)
    httpProfile = HttpProfile()
    httpProfile.endpoint = "teo.tencentcloudapi.com"
    clientProfile = ClientProfile()
    clientProfile.httpProfile = httpProfile
    common_client = CommonClient("teo", "2022-09-01", cred, "", profile=clientProfile)
    debug("action=%s, params=%s", action, params)
    try:
        return common_client.call_json(action, params)["Response"]
    except TencentCloudSDKException as e:
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
            "Origin": ip
        },
        "HttpOriginPort": port,
        "HttpsOriginPort": port,
    }
    return request("ModifyAccelerationDomain", payload)
