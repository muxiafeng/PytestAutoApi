#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time   : 2022/3/30 14:12
# @Author : 余少琪
import ast
import json
import time

import allure
import pytest
import requests

from common.setting import ensure_path_sep
from utils.cache_process.cache_control import CacheHandler
from utils.logging_tool.log_control import INFO, ERROR, WARNING
from utils.other_tools.allure_data.allure_tools import allure_step, allure_step_no
from utils.other_tools.models import TestCase
from utils.read_files_tools.clean_files import del_file
from utils.requests_tool.request_control import cache_regular


@pytest.fixture(scope="session", autouse=False)
def clear_report():
    """如clean命名无法删除报告，这里手动删除"""
    del_file(ensure_path_sep("\\report"))


@pytest.fixture(scope="session", autouse=False)
def work_login_init1():
    """
    获取登录的cookie
    :return:
    """

    url = "http://121.37.220.0:5000/login"
    data = """{
        "username": "user2",
        "password": "password2"
    }"""
    headers = {'Content-Type': 'application/json'}
    # 请求登录接口

    res = requests.post(url=url, data=data, verify=True, headers=headers)
    response_cookie = res.cookies
    # print('获取的cookie为：', res.cookies)

    cookies = ''
    for k, v in response_cookie.items():
        _cookie = k + "=" + v + ";"
        # 拿到登录的cookie内容，cookie拿到的是字典类型，转换成对应的格式
        cookies += _cookie
        # 将登录接口中的cookie写入缓存中，其中login_cookie是缓存名称
    CacheHandler.update_cache(cache_name='login_cookie', value=cookies)


@pytest.fixture(scope="session", autouse=True)
def work_login_init():
    """
    获取登录的cookie
    :return:
    """

    url = "http://121.37.220.0:1157/api/account/auth/form"
    payload = json.dumps({
        "type": 0,
        "identifier": "admin",
        "credential": "hertzbeat"
    })
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'zh-CN',
        'Content-Type': 'application/json',
        'Cookie': '_ga=GA1.1.49248213.1724726403; _ga_13PPZZ7P4Y=GS1.1.1724726402.1.1.1724726420.0.0.0; _dd_s=logs=1&id=4cb400da-fbfd-46d2-a562-a047a4557663&created=1724726401215&expire=1724727341593; base64=dXNlcjJsb2dpblN1Y2Nlc3M=',
        'Origin': 'http://121.37.220.0:1157',
        'Proxy-Connection': 'keep-alive',
        'Referer': 'http://121.37.220.0:1157/passport/login',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36'
    }
    # 请求登录接口

    res = requests.request("POST", url, headers=headers, data=payload)
    token = (json.loads(res.content))['data']['token']
    # print(res.text)

    cookies = 'Bearer ' + token
    # print(cookies)
    # for k, v in response_cookie.items():
    #     _cookie = k + "=" + v + ";"
    #     # 拿到登录的cookie内容，cookie拿到的是字典类型，转换成对应的格式
    #     cookies += _cookie
    #     # 将登录接口中的cookie写入缓存中，其中login_cookie是缓存名称
    CacheHandler.update_cache(cache_name='login_cookie', value=cookies)


def pytest_collection_modifyitems(items):
    """
    测试用例收集完成时，将收集到的 item 的 name 和 node_id 的中文显示在控制台上
    :return:
    """
    for item in items:
        item.name = item.name.encode("utf-8").decode("unicode_escape")
        item._nodeid = item.nodeid.encode("utf-8").decode("unicode_escape")

    # 期望用例顺序
    # print("收集到的测试用例:%s" % items)
    appoint_items = ["test_get_user_info", "test_collect_addtool", "test_Cart_List", "test_ADD", "test_Guest_ADD",
                     "test_Clear_Cart_Item"]

    # 指定运行顺序
    run_items = []
    for i in appoint_items:
        for item in items:
            module_item = item.name.split("[")[0]
            if i == module_item:
                run_items.append(item)

    for i in run_items:
        run_index = run_items.index(i)
        items_index = items.index(i)

        if run_index != items_index:
            n_data = items[run_index]
            run_index = items.index(n_data)
            items[items_index], items[run_index] = items[run_index], items[items_index]


def pytest_configure(config):
    config.addinivalue_line("markers", 'smoke')
    config.addinivalue_line("markers", '回归测试')


@pytest.fixture(scope="function", autouse=True)
def case_skip(in_data):
    """处理跳过用例"""
    in_data = TestCase(**in_data)
    if ast.literal_eval(cache_regular(str(in_data.is_run))) is False:
        allure.dynamic.title(in_data.detail)
        allure_step_no(f"请求URL: {in_data.is_run}")
        allure_step_no(f"请求方式: {in_data.method}")
        allure_step("请求头: ", in_data.headers)
        allure_step("请求数据: ", in_data.data)
        allure_step("依赖数据: ", in_data.dependence_case_data)
        allure_step("预期数据: ", in_data.assert_data)
        pytest.skip()


def pytest_terminal_summary(terminalreporter):
    """
    收集测试结果
    """

    _PASSED = len([i for i in terminalreporter.stats.get('passed', []) if i.when != 'teardown'])
    _ERROR = len([i for i in terminalreporter.stats.get('error', []) if i.when != 'teardown'])
    _FAILED = len([i for i in terminalreporter.stats.get('failed', []) if i.when != 'teardown'])
    _SKIPPED = len([i for i in terminalreporter.stats.get('skipped', []) if i.when != 'teardown'])
    _TOTAL = terminalreporter._numcollected
    _TIMES = time.time() - terminalreporter._sessionstarttime
    INFO.logger.error(f"用例总数: {_TOTAL}")
    INFO.logger.error(f"异常用例数: {_ERROR}")
    ERROR.logger.error(f"失败用例数: {_FAILED}")
    WARNING.logger.warning(f"跳过用例数: {_SKIPPED}")
    INFO.logger.info("用例执行时长: %.2f" % _TIMES + " s")

    try:
        _RATE = _PASSED / _TOTAL * 100
        INFO.logger.info("用例成功率: %.2f" % _RATE + " %")
    except ZeroDivisionError:
        INFO.logger.info("用例成功率: 0.00 %")

if __name__ == '__main__':
    work_login_init()