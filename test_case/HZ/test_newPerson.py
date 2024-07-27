#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time   : 2024-07-26 14:58:10


import allure
import pytest
from utils.read_files_tools.get_yaml_data_analysis import GetTestCase
from utils.assertion.assert_control import Assert
from utils.requests_tool.request_control import RequestControl
from utils.read_files_tools.regular_control import regular
from utils.requests_tool.teardown_control import TearDownHandler


case_id = ['new_person_01', 'new_person_02', 'new_person_03', 'new_person_04', 'new_person_05']
TestData = GetTestCase.case_data(case_id)
re_data = regular(str(TestData))


@allure.epic("测试项目")
@allure.feature("基础模块")
class TestNewperson:

    @allure.story("个人信息展示")
    @pytest.mark.parametrize('in_data', eval(re_data), ids=[i['detail'] for i in TestData])
    def test_newPerson(self, in_data, case_skip):
        """
        :param :
        :return:
        """
        res = RequestControl(in_data).http_request()
        TearDownHandler(res).teardown_handle()
        Assert(in_data['assert_data']).assert_equality(response_data=res.response_data,
                                                       sql_data=res.sql_data, status_code=res.status_code)


if __name__ == '__main__':
    pytest.main(['test_newPerson.py', '-s', '-W', 'ignore:Module already imported:pytest.PytestWarning'])
    # pytest.main(['test_newPerson.py', '-q', '-W', 'ignore:Module already imported:pytest.PytestWarning'])
