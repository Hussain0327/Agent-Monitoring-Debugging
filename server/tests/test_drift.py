"""Tests for drift detection endpoints."""

from __future__ import annotations

import pytest

from vigil_server.services.drift_detector import compute_psi, severity_from_psi


class TestDriftAlerts:
    async def test_alerts_empty(self, client):
        res = await client.get("/v1/drift/alerts")
        assert res.status_code == 200
        assert res.json() == []

    async def test_summary_empty(self, client):
        res = await client.get("/v1/drift/summary")
        assert res.status_code == 200
        data = res.json()
        assert data["total_alerts"] == 0
        assert data["unresolved"] == 0


class TestPSIComputation:
    def test_identical_distributions(self):
        baseline = [1.0, 2.0, 3.0, 4.0, 5.0] * 10
        current = [1.0, 2.0, 3.0, 4.0, 5.0] * 10
        psi = compute_psi(baseline, current)
        assert psi < 0.1

    def test_different_distributions(self):
        baseline = [1.0, 1.1, 1.2, 1.3, 1.4] * 10
        current = [5.0, 5.1, 5.2, 5.3, 5.4] * 10
        psi = compute_psi(baseline, current)
        assert psi > 0.1

    def test_empty_inputs(self):
        assert compute_psi([], [1.0, 2.0]) == 0.0
        assert compute_psi([1.0, 2.0], []) == 0.0

    def test_zero_variance(self):
        assert compute_psi([1.0] * 10, [1.0] * 10) == 0.0


class TestSeverityFromPSI:
    def test_low(self):
        assert severity_from_psi(0.05) == "low"

    def test_medium(self):
        assert severity_from_psi(0.15) == "medium"

    def test_high(self):
        assert severity_from_psi(0.25) == "high"
