#!/usr/bin/env python3
"""Aplica o patch do botão "Reiniciar jogo" num HTML exportado pelo TurboWarp Packager.

O botão é flutuante, fixo na lateral direita do palco (fora do canvas, sobre a
faixa preta do letterbox), e chama scaffolding.greenFlag() — o mesmo que clicar
na bandeira verde: para tudo e recomeça o jogo.

Uso:
    python3 add_restart_button.py [caminho/do/index.html]

Idempotente: se o botão já existir, não altera nada.
"""
import pathlib
import sys

CSS_ANCHOR = "    .fullscreen-button {\n      background: white;\n    }"
CSS_PATCH = """    #restart-button {
      position: fixed;
      right: 10px;
      top: 50%;
      transform: translateY(-50%);
      width: 48px;
      height: 48px;
      border-radius: 50%;
      border: none;
      background: rgba(255, 76, 76, 0.92);
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.5);
      display: flex;
      align-items: center;
      justify-content: center;
      cursor: pointer;
      z-index: 9999;
      padding: 0;
    }
    #restart-button:active {
      background: rgba(201, 58, 58, 0.95);
    }
    #restart-button svg {
      display: block;
      pointer-events: none;
    }
"""

SCRIPT_ANCHOR = "  <script>\n    const run = async () => {"
SCRIPT_PATCH = """  <script>
    // Botão "Reiniciar jogo" (wrapper APK): flutua ao lado do palco,
    // equivale a clicar na bandeira verde.
    (function() {
      function addRestartButton() {
        var sc = window.scaffolding;
        var loading = document.getElementById('loading');
        var ready = sc && typeof sc.greenFlag === 'function' && (!loading || loading.hidden);
        if (!ready) {
          setTimeout(addRestartButton, 300);
          return;
        }
        if (document.getElementById('restart-button')) return;
        var btn = document.createElement('button');
        btn.id = 'restart-button';
        btn.title = 'Reiniciar jogo';
        btn.setAttribute('aria-label', 'Reiniciar jogo');
        btn.innerHTML = '<svg width="24" height="24" viewBox="0 0 24 24"><path fill="#ffffff" d="M17.65 6.35C16.2 4.9 14.21 4 12 4c-4.42 0-7.99 3.58-7.99 8s3.57 8 7.99 8c3.73 0 6.84-2.55 7.73-6h-2.08c-.82 2.33-3.04 4-5.65 4-3.31 0-6-2.69-6-6s2.69-6 6-6c1.66 0 3.14.69 4.22 1.78L13 11h7V4l-2.35 2.35z"/></svg>';
        btn.addEventListener('click', function() {
          try { sc.greenFlag(); } catch (e) { console.error(e); }
        });
        document.body.appendChild(btn);
      }
      addRestartButton();
    })();
  </script>
"""

MARKER = 'id="restart-button"'


def patch(path: pathlib.Path) -> bool:
    t = path.read_text(encoding="utf-8")
    if MARKER in t and "#restart-button" in t:
        print("Botão já existe, nada a fazer.")
        return False
    if CSS_ANCHOR not in t:
        raise SystemExit("Âncora CSS não encontrada — HTML não é do TurboWarp Packager?")
    if SCRIPT_ANCHOR not in t:
        raise SystemExit("Âncora de script não encontrada — HTML não é do TurboWarp Packager?")
    t = t.replace(CSS_ANCHOR, CSS_PATCH + CSS_ANCHOR, 1)
    t = t.replace(SCRIPT_ANCHOR, SCRIPT_PATCH + SCRIPT_ANCHOR, 1)
    path.write_text(t, encoding="utf-8")
    print(f"Patch aplicado em {path}")
    return True


if __name__ == "__main__":
    target = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path(
        "../app/src/main/assets/www/index.html"
    ).resolve()
    patch(target)
