# Tests de main.py sin modificarlo: arranque real vía runpy (D10)
import logging
import runpy
from pathlib import Path

import pytest

import ui.menu as menu_modulo

RAIZ = Path(__file__).resolve().parents[2]
MAIN = RAIZ / "main.py"


def entrada_secuencial(monkeypatch, *valores):
    pendientes = list(valores)

    def _input(prompt=""):
        if not pendientes:
            raise AssertionError(f"Se agotaron las entradas (prompt: {prompt!r})")
        return pendientes.pop(0)

    monkeypatch.setattr("builtins.input", _input)


def test_setup_logging_configura_nivel_y_formato(monkeypatch):
    import main

    capturado = {}

    def fake_basicConfig(**kwargs):
        capturado.update(kwargs)

    monkeypatch.setattr(main.logging, "basicConfig", fake_basicConfig)

    main.setup_logging()

    assert capturado["level"] == logging.DEBUG
    assert capturado["format"] == "%(levelname)s %(name)s: %(message)s"


def test_arranque_y_salida_normal(monkeypatch, capsys):
    entrada_secuencial(monkeypatch, "12")
    monkeypatch.setattr("os.system", lambda comando: 0)
    monkeypatch.setattr("time.sleep", lambda segundos: None)

    runpy.run_path(str(MAIN), run_name="__main__")

    salida = capsys.readouterr().out
    assert "SISTEMA DE PELÍCULAS Y SERIES" in salida
    assert "¡Hasta luego!" in salida


def test_interrupcion_del_teclado_sale_con_codigo_cero(monkeypatch, capsys):
    def interrumpir():
        raise KeyboardInterrupt

    monkeypatch.setattr(menu_modulo, "menu_principal", interrumpir)
    monkeypatch.setattr("os.system", lambda comando: 0)

    with pytest.raises(SystemExit) as excinfo:
        runpy.run_path(str(MAIN), run_name="__main__")

    assert excinfo.value.code == 0
    assert "Programa interrumpido" in capsys.readouterr().out


def test_error_inesperado_sale_con_codigo_uno(monkeypatch, capsys, caplog):
    def fallar():
        raise RuntimeError("boom")

    monkeypatch.setattr(menu_modulo, "menu_principal", fallar)
    monkeypatch.setattr("os.system", lambda comando: 0)

    with caplog.at_level(logging.ERROR, logger="main"):
        with pytest.raises(SystemExit) as excinfo:
            runpy.run_path(str(MAIN), run_name="__main__")

    assert excinfo.value.code == 1
    assert "Error inesperado: boom" in capsys.readouterr().out
    assert "Error inesperado" in caplog.text
