# Barrera de red: ningún test unitario puede hacer peticiones reales (Fase 6)
import pytest
import requests


@pytest.fixture(autouse=True)
def sin_internet(monkeypatch):
    """Corta cualquier petición HTTP real dentro de tests/unit/"""

    def _bloqueado(*args, **kwargs):
        raise AssertionError("Los tests unitarios no deben acceder a Internet")

    monkeypatch.setattr(requests.sessions.Session, "request", _bloqueado)
