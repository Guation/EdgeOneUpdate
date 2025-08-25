#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# https://github.com/Guation/EdgeOneUpdate

__author__ = "Guation"

import os, argparse, sys, json, traceback, socket, time, threading, multiprocessing
from logging import debug, info, warning, error, DEBUG, INFO, basicConfig
from edgeone_update.edgeone_api import init
from edgeone_update.http_server import run_server
from edgeone_update.version import VERSION
from edgeone_update.addr_tool import convert_addr

def register_exit():
    import signal
    force_exit = False
    def stop(signum, frame):
        nonlocal force_exit
        if force_exit:
            warning("强制退出")
            os._exit(1)
        else:
            info("用户退出")
            force_exit = True
            sys.exit(0)
    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)

def init_logger(debug: bool) -> None:
    if debug:
        basicConfig(
            level=DEBUG,
            format='[%(levelname)8s] %(asctime)s <%(module)s.%(funcName)s>:%(lineno)d\n[%(levelname)8s] %(message)s')
    else:
        basicConfig(
            level=INFO,
            format='[%(levelname)8s] %(message)s')

def main():
    parser = argparse.ArgumentParser(description='EdgeOneUpdate', add_help=False, allow_abbrev=False, usage=argparse.SUPPRESS)
    parser.add_argument('-h', '--help', dest='H', action='store_true')
    parser.add_argument('-c', '--config', dest='C', type=str, default="config.json")
    parser.add_argument('-d', '--debug', dest='D', action='store_true')
    parser.add_argument('-v', '--version', dest='V', action='store_true')
    args = parser.parse_args()

    init_logger(args.D)

    if args.H:
        info(
            "\n%s [-h] [-l] [-c] [-d] [-v]"
            "\n-h  --help                              显示本帮助"
            "\n-c  --config <config.json>              DDNS配置文件，不指定时默认为当前目录的config.json"
            "\n-d  --debug                             Debug模式"
            "\n-v  --version                           显示版本"
            "\n"
            "\nconfig.json 详见README"
            "\nid(String|null)"
            "\ntoken(String|null)"
            "\ndomain(String)"
            "\nsub_domain(String)"
            "\nlocal(String|null)"
        , sys.argv[0])
        sys.exit(0)
    if args.V:
        info(VERSION)
        sys.exit(0)
    config = {
        "id": "",
        "token": "",
        "domain": "",
        "sub_domain": "",
        "local": ":8080"
    }
    if not os.path.isfile(args.C):
        error("EdgeOne配置文件 %s 未找到" , os.path.abspath(args.C))
        try:
            if sys.stdin.isatty():
                gen_config = input("是否生成新配置[y/N]：")
                if gen_config.upper().startswith("Y"):
                    with open(args.C, "w") as f:
                        f.write(json.dumps(config, indent=4, ensure_ascii=False))
                        f.flush()
                    info("EdgeOne配置文件 %s 已生成" , os.path.abspath(args.C))
        except (EOFError, OSError):
            debug(traceback.format_exc())
        sys.exit(1)
    try:
        with open(args.C, "r") as f:
            config_s1 = f.read()
            config.update(json.loads(config_s1))
    except Exception:
        error("EdgeOne配置文件 %s 读取失败", os.path.abspath(args.C))
        debug(traceback.format_exc())
        sys.exit(1)
    try:
        config_s2 = json.dumps(config, indent=4, ensure_ascii=False)
        if config_s1 != config_s2:
            with open(args.C, "w") as f:
                f.write(config_s2)
                f.flush()
    except Exception:
        warning("EdgeOne配置文件 %s 回写失败", os.path.abspath(args.C))
        debug(traceback.format_exc())
    init(config["id"], config["token"], config["sub_domain"], config["domain"])
    try:
        local_addr = convert_addr(config["local"], "0.0.0.0")
        assert local_addr
    except (ValueError, AssertionError) as e:
        error("config 中 local 字段解析错误: %s", e)
        debug(traceback.format_exc())
        sys.exit(1)
    register_exit()
    run_server(*local_addr)
