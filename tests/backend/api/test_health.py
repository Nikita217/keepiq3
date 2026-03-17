import importlib.util

import pytest

if importlib.util.find_spec('jwt') is None:
    pytest.skip('PyJWT is not installed in this environment.', allow_module_level=True)

from fastapi.testclient import TestClient

from app.main import app


def test_healthcheck_route():
    client = TestClient(app)
    response = client.get('/api/v1/health')

    assert response.status_code == 200
    assert response.json() == {'status': 'ok'}
