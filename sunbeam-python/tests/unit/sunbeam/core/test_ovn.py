# SPDX-FileCopyrightText: 2026 - Canonical Ltd
# SPDX-License-Identifier: Apache-2.0

import pytest

from sunbeam.core.ovn import (
    DEFAULT_ARCHITECTURE,
    MICROOVN_APPLICATION,
    microovn_application_name_for_node,
)


class TestMicroovnApplicationNameForNode:
    def test_default_architecture_uses_default_application(self):
        node = {"arch": DEFAULT_ARCHITECTURE}

        assert microovn_application_name_for_node(node) == MICROOVN_APPLICATION

    def test_missing_architecture_defaults_to_default_application(self):
        node = {}

        assert microovn_application_name_for_node(node) == MICROOVN_APPLICATION

    def test_empty_architecture_defaults_to_default_application(self):
        node = {"arch": ""}

        assert microovn_application_name_for_node(node) == MICROOVN_APPLICATION

    def test_non_default_architecture_uses_per_arch_application(self):
        node = {"arch": "arm64"}

        assert (
            microovn_application_name_for_node(node) == f"{MICROOVN_APPLICATION}-arm64"
        )

    @pytest.mark.parametrize("is_dpu", [True, False])
    def test_grouping_is_independent_of_is_dpu(self, is_dpu):
        # Application selection is purely architecture based; is_dpu must not
        # change the result.
        amd64_node = {"arch": DEFAULT_ARCHITECTURE, "is_dpu": is_dpu}
        arm64_node = {"arch": "arm64", "is_dpu": is_dpu}

        assert microovn_application_name_for_node(amd64_node) == MICROOVN_APPLICATION
        assert (
            microovn_application_name_for_node(arm64_node)
            == f"{MICROOVN_APPLICATION}-arm64"
        )
