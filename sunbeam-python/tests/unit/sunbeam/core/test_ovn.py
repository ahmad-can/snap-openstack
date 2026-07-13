# SPDX-FileCopyrightText: 2026 - Canonical Ltd
# SPDX-License-Identifier: Apache-2.0

from unittest.mock import Mock, patch

from sunbeam.core import ovn


def test_get_machines_by_architecture_groups_valid_microovn_machine_ids():
    client = Mock()
    client.cluster.list_nodes_by_role.side_effect = lambda role: {
        "network": [
            {"name": "network-1", "machineid": 2},
            {"name": "dpu-1", "machineid": 52, "arch": "arm64"},
            {"name": "pending", "machineid": -1, "arch": "arm64"},
        ],
        "compute": [
            {"name": "compute-1", "machineid": 1, "arch": "amd64"},
            {"name": "compute-2", "machineid": 1, "arch": "amd64"},
        ],
        "control": [
            {"name": "control-1", "machineid": None, "arch": "amd64"},
            {"name": "dpu-2", "machineid": 53, "arch": "arm64"},
        ],
    }[role]
    manager = ovn.OvnManager(client)

    with patch(
        "sunbeam.core.ovn.load_provider_config",
        return_value=ovn.OvnConfig(provider=ovn.OvnProvider.MICROOVN),
    ):
        machines_by_arch = manager.get_machines_by_architecture()

    assert machines_by_arch == {
        "amd64": ["1", "2"],
        "arm64": ["52", "53"],
    }


def test_get_token_distributor_machines_prefers_control_for_microovn():
    client = Mock()
    client.cluster.list_nodes_by_role.side_effect = lambda role: {
        "network": [
            {"name": "dpu-1", "machineid": 52, "arch": "arm64"},
            {"name": "network-1", "machineid": 3, "arch": "amd64"},
        ],
        "compute": [
            {"name": "compute-1", "machineid": 2, "arch": "amd64"},
        ],
        "control": [
            {"name": "control-1", "machineid": 1, "arch": "amd64"},
            {"name": "pending", "machineid": -1, "arch": "amd64"},
        ],
    }[role]
    manager = ovn.OvnManager(client)

    with patch(
        "sunbeam.core.ovn.load_provider_config",
        return_value=ovn.OvnConfig(provider=ovn.OvnProvider.MICROOVN),
    ):
        machines = manager.get_token_distributor_machines()

    assert machines == ["1"]


def test_get_token_distributor_machines_can_override_provider():
    client = Mock()
    client.cluster.list_nodes_by_role.side_effect = lambda role: {
        "network": [
            {"name": "dpu-1", "machineid": 52, "arch": "arm64"},
        ],
        "compute": [
            {"name": "compute-1", "machineid": 2, "arch": "amd64"},
        ],
        "control": [
            {"name": "control-1", "machineid": 1, "arch": "amd64"},
        ],
    }[role]
    manager = ovn.OvnManager(client)

    with patch(
        "sunbeam.core.ovn.load_provider_config",
        return_value=ovn.OvnConfig(provider=ovn.OvnProvider.OVN_K8S),
    ):
        machines = manager.get_token_distributor_machines(
            provider=ovn.OvnProvider.MICROOVN
        )

    assert machines == ["1"]


def test_get_token_distributor_machines_uses_network_for_ovn_k8s():
    client = Mock()
    client.cluster.list_nodes_by_role.side_effect = lambda role: {
        "network": [
            {"name": "network-1", "machineid": 3, "arch": "amd64"},
        ],
        "compute": [
            {"name": "compute-1", "machineid": 2, "arch": "amd64"},
        ],
        "control": [
            {"name": "control-1", "machineid": 1, "arch": "amd64"},
        ],
    }[role]
    manager = ovn.OvnManager(client)

    with patch(
        "sunbeam.core.ovn.load_provider_config",
        return_value=ovn.OvnConfig(provider=ovn.OvnProvider.OVN_K8S),
    ):
        machines = manager.get_token_distributor_machines()

    assert machines == ["3"]
