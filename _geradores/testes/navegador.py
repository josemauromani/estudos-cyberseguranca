"""Harness de navegador: executa uma página no Chrome headless e devolve o resultado de um script de teste."""

import html as html_lib
import json
import os
import re
import signal
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Optional

CHROME = shutil.which("google-chrome") or shutil.which("chromium")

_COLETOR = """<script>
window.__erros = [];
window.onerror = function (msg) { window.__erros.push(String(msg)); };
window.addEventListener('unhandledrejection', function (e) { window.__erros.push('rejeicao: ' + String(e.reason)); });
(function () {
  var original = console.error;
  console.error = function () {
    window.__erros.push(Array.prototype.map.call(arguments, String).join(' '));
    return original.apply(console, arguments);
  };
})();
window.__fim = function (valor) {
  if (document.getElementById('__saida')) return;
  var saida = valor === undefined ? null : valor;
  var pre = document.createElement('pre');
  pre.id = '__saida';
  pre.textContent = JSON.stringify({ saida: saida, erros: window.__erros });
  document.documentElement.appendChild(pre);
  // Erros assíncronos tardios: reescreve a saída com os erros acumulados depois do __fim.
  setTimeout(function () {
    pre.textContent = JSON.stringify({ saida: saida, erros: window.__erros });
  }, 300);
};
</script>"""

_SAIDA = re.compile(r'<pre id="__saida">(.*?)</pre>', re.S)


def executar(
    html: str,
    script_teste: str = "",
    perfil: Optional[Path] = None,
    largura: int = 1440,
    altura: int = 900,
    budget_ms: int = 4000,
    script_antes: str = "",
) -> dict:
    """Roda `html` no Chrome headless e devolve {"saida": valor, "erros": [...]}.

    `script_antes` roda no início do <head>, antes de qualquer script da página.
    `script_teste` roda após DOMContentLoaded (depois da inicialização do base.js)
    e deve terminar chamando `__fim(valor)`.
    """
    if not CHROME:
        raise RuntimeError("Chrome não encontrado")

    antes = f"<script>{script_antes}</script>" if script_antes else ""
    injetado = html.replace("<head>", "<head>" + _COLETOR + antes, 1)
    if script_teste:
        teste = (
            "<script>document.addEventListener('DOMContentLoaded', function () {"
            "try {\n" + script_teste + "\n} catch (e) { window.__erros.push('teste: ' + e); __fim(null); }"
            "});</script>"
        )
        indice = injetado.rfind("</body>")
        injetado = injetado[:indice] + teste + injetado[indice:]

    with tempfile.TemporaryDirectory() as pasta:
        arquivo = Path(pasta) / "pagina.html"
        arquivo.write_text(injetado, encoding="utf-8")
        with tempfile.TemporaryDirectory() as perfil_tmp:
            comando = [
                CHROME,
                "--headless=new",
                "--disable-gpu",
                "--no-sandbox",
                "--no-first-run",
                f"--user-data-dir={perfil if perfil else perfil_tmp}",
                f"--window-size={largura},{altura}",
                f"--virtual-time-budget={budget_ms}",
                "--dump-dom",
                arquivo.as_uri(),
            ]
            # Sessão própria: no timeout, mata o grupo inteiro (o Chrome gera vários processos).
            proc = subprocess.Popen(
                comando, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, start_new_session=True
            )
            try:
                saida_chrome, erro_chrome = proc.communicate(timeout=90)
            except subprocess.TimeoutExpired:
                os.killpg(proc.pid, signal.SIGKILL)
                proc.communicate()
                raise
            finally:
                try:
                    os.killpg(proc.pid, signal.SIGKILL)
                except (ProcessLookupError, PermissionError):
                    pass

    achado = _SAIDA.search(saida_chrome)
    if not achado:
        raise RuntimeError(
            "O script de teste não chamou __fim(); saída do Chrome:\n" + saida_chrome[-800:] + erro_chrome[-400:]
        )
    return json.loads(html_lib.unescape(achado.group(1)))
