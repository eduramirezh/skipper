#!/usr/bin/env python
# -*- coding: utf-8

# Copyright 2017-2019 The FIAAS Authors
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#      http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import pytest
from k8s.models.common import ObjectMeta
from k8s.models.configmap import ConfigMap
from mock import mock

from fiaas_skipper.deploy.cluster import Cluster

NAME = "deployment_target"


def _create_configmap(namespace, tag=None):
    metadata = ObjectMeta(name=NAME, namespace=namespace)
    data = {}
    if tag:
        data["tag"] = tag
    return ConfigMap(metadata=metadata, data=data)


def _assert_deployment_config(result, namespace, tag):
    assert namespace == result.namespace
    assert tag == result.tag


class TestCluster(object):
    @pytest.fixture
    def config_map_find(self):
        with mock.patch("k8s.models.configmap.ConfigMap.find") as finder:
            finder.return_value = (
                _create_configmap("ns1", "stable"),
                _create_configmap("ns2", "latest"),
                _create_configmap("ns3"),
                _create_configmap("ns4", "latest"),
                _create_configmap("ns5", "stable"),
            )
            yield finder

    @pytest.mark.usefixtures("config_map_find")
    def test_finds_deployment_configs(self):
        cluster = Cluster()
        results = cluster.find_deployment_configs(NAME)

        assert len(results) == 5
        _assert_deployment_config(results[0], "ns1", "stable")
        _assert_deployment_config(results[1], "ns2", "latest")
        _assert_deployment_config(results[2], "ns3", "stable")
