#!/usr/bin/env python3
"""Injeta o botao de relato (erro / sugestao) em uma pagina publicada.

Uma barra no alto e outra embaixo, em branco e vermelho, abrindo um formulario
que entrega a mensagem por relay de formulario. Sem dependencia externa.

Uso:  python3 relatar.py <arquivo.html> [<arquivo.html> ...]

A injecao e idempotente: um arquivo que ja carrega o widget e devolvido intacto.
"""
import re
import sys

# Identificador publico do relay, nao credencial: qualquer visitante que abrir o
# codigo-fonte da pagina o le. Trocar o destino e trocar esta constante e
# republicar. Declarado no registro de acesso do projeto (linhas Web3Forms).
CHAVE_RELAY = "596b7023-f2a3-4f29-8f0b-fb446fad4664"
ENDPOINT_RELAY = "https://api.web3forms.com/submit"

MARCA = "relatar-widget"

CSS = """
/* ---------- barra de relato (branco e vermelho) ---------- */
.rbar{ --r:#c1121f; --r-fundo:#ffffff; --r-borda:#e8b4b2;
  max-width:var(--rw, 68rem); margin:2.25rem auto; padding-inline:clamp(.75rem,3vw,1.25rem); }
.rbar-in{ display:flex; flex-wrap:wrap; align-items:center; justify-content:space-between;
  gap:.85rem 1.25rem; background:var(--r-fundo); border:2px solid var(--r);
  border-radius:.6rem; padding:.95rem 1.15rem; }
.rbar-t{ margin:0; color:var(--r); font-weight:600; font-size:.95rem; line-height:1.35; }
.rbar-t small{ display:block; font-weight:400; font-size:.82rem; color:#8c3b36; margin-top:.15rem; }
.rbtn{ font:inherit; font-size:.9rem; font-weight:600; cursor:pointer; white-space:nowrap;
  border:2px solid #c1121f; border-radius:.45rem; padding:.55rem 1.05rem;
  background:#c1121f; color:#fff; }
.rbtn:hover{ background:#fff; color:#c1121f; }
.rbtn:focus-visible{ outline:3px solid #c1121f; outline-offset:2px; }
.rbtn.ghost{ background:#fff; color:#c1121f; }
.rbtn.ghost:hover{ background:#f7e6e6; }
.rdlg{ border:2px solid #c1121f; border-radius:.7rem; padding:0; max-width:34rem; width:calc(100% - 2rem);
  background:#fff; color:#16181c; }
.rdlg::backdrop{ background:rgba(16,18,22,.55); }
.rdlg form{ padding:1.25rem 1.35rem 1.1rem; }
.rdlg h2{ margin:0 0 .35rem; font-size:1.1rem; color:#c1121f; }
.rnote{ margin:0 0 1rem; font-size:.85rem; line-height:1.5; color:#5c616b; }
.rdlg label{ display:block; font-size:.82rem; font-weight:600; color:#16181c; margin-bottom:.85rem; }
.rdlg textarea,.rdlg input[type=email],.rdlg select{ display:block; width:100%; box-sizing:border-box;
  margin-top:.3rem; font:inherit; font-size:.9rem; font-weight:400; color:#16181c; background:#fff;
  border:1px solid #c9ccd2; border-radius:.35rem; padding:.5rem .6rem; }
.rdlg textarea:focus,.rdlg input:focus,.rdlg select:focus{ outline:2px solid #c1121f; outline-offset:1px; }
.ract{ display:flex; gap:.6rem; justify-content:flex-end; margin:.25rem 0 0; }
.rstatus{ margin:.75rem 0 0; font-size:.85rem; min-height:1.2em; color:#5c616b; }
.rstatus.erro{ color:#c1121f; font-weight:600; }
.rstatus.ok{ color:#2c6543; font-weight:600; }
.rhp{ position:absolute; left:-9999px; width:1px; height:1px; opacity:0; }
@media (max-width:30rem){ .rbar-in{ flex-direction:column; align-items:stretch; } .rbtn{ width:100%; } }
"""

BARRA = """
<div class="rbar" data-relatar-barra>
  <div class="rbar-in">
    <p class="rbar-t">Achou um erro? Tem uma sugestão?
      <small>Todo número desta página é reproduzível — e contestável. Diga onde erramos.</small></p>
    <button type="button" class="rbtn" data-relatar>Relatar erro ou sugestão</button>
  </div>
</div>
"""

DIALOGO = """
<dialog class="rdlg" id="rdlg">
  <form id="rform" novalidate>
    <h2>Relatar erro ou sugestão</h2>
    <p class="rnote">Vai direto para quem mantém este relatório. Esta página não guarda
      nem lê o que você escrever — a mensagem sai do seu navegador para o canal de
      contato e nada fica registrado aqui.</p>
    <label for="rtipo">Tipo
      <select id="rtipo" name="tipo">
        <option>Erro nos dados</option>
        <option>Erro de interpretação</option>
        <option>Sugestão</option>
        <option>Outro</option>
      </select></label>
    <label for="rmsg">Mensagem
      <textarea id="rmsg" name="message" rows="6" required
        placeholder="Onde está o erro, ou o que deveria existir aqui e não existe."></textarea></label>
    <label for="rmail">Seu e-mail (opcional, para resposta)
      <input id="rmail" name="email" type="email" autocomplete="email"></label>
    <input type="checkbox" name="botcheck" class="rhp" tabindex="-1" autocomplete="off" aria-hidden="true">
    <p class="ract">
      <button type="button" class="rbtn ghost" data-fechar>Cancelar</button>
      <button type="submit" class="rbtn">Enviar</button></p>
    <p class="rstatus" role="status"></p>
  </form>
</dialog>
"""

JS = """
<script id="relatar-widget">
/* ---------- barra de relato: abrir, enviar, fechar ---------- */
(function () {
  var CHAVE = "%(chave)s", ENDPOINT = "%(endpoint)s";
  var dlg = document.getElementById('rdlg');
  var form = document.getElementById('rform');
  if (!dlg || !form) { return; }
  var status = form.querySelector('.rstatus');
  var enviar = form.querySelector('button[type=submit]');

  function dizer(txt, classe) { status.className = 'rstatus' + (classe ? ' ' + classe : ''); status.textContent = txt; }

  document.addEventListener('click', function (ev) {
    var abre = ev.target.closest('[data-relatar]');
    if (abre) { dizer(''); if (dlg.showModal) { dlg.showModal(); } else { dlg.setAttribute('open', ''); }
      var m = document.getElementById('rmsg'); if (m) { m.focus(); } return; }
    if (ev.target.closest('[data-fechar]')) { if (dlg.close) { dlg.close(); } else { dlg.removeAttribute('open'); } }
  });

  form.addEventListener('submit', function (ev) {
    ev.preventDefault();
    if (form.botcheck.checked) { dizer('Mensagem enviada. Obrigado.', 'ok'); form.reset(); return; }
    var msg = form.message.value.trim();
    if (!msg) { dizer('Escreva a mensagem antes de enviar.', 'erro'); form.message.focus(); return; }
    var corpo = { access_key: CHAVE, message: msg, email: form.email.value,
      subject: 'Relato — ' + form.tipo.value + ' — ' + document.title,
      from_name: 'Relatórios CLDF', tipo: form.tipo.value,
      pagina: location.href, titulo: document.title };
    enviar.disabled = true; dizer('Enviando…');
    fetch(ENDPOINT, { method: 'POST',
      headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
      body: JSON.stringify(corpo) })
      .then(function (r) { return r.json(); })
      .then(function (j) {
        enviar.disabled = false;
        if (j.success) { dizer('Mensagem enviada. Obrigado.', 'ok'); form.reset(); }
        else { dizer('Não foi possível enviar: ' + (j.message || 'erro desconhecido') + '.', 'erro'); }
      })
      .catch(function (e) { enviar.disabled = false;
        dizer('Não foi possível enviar: ' + e.message + '.', 'erro'); });
  });
})();
</script>
""" % {"chave": CHAVE_RELAY, "endpoint": ENDPOINT_RELAY}


def injetar(html: str) -> str:
    """Devolve a pagina com a barra no alto, a barra embaixo e o formulario.

    Idempotente: se a marca ja estiver presente, devolve o original intacto.
    """
    if MARCA in html:
        return html

    # 1. o CSS entra no bloco <style> que a propria pagina ja carrega
    i = html.index("</style>")
    html = html[:i] + CSS + html[i:]

    # 2. a barra do alto, logo dentro do container principal
    m = re.search(r'<div class="wrap">', html)
    if m:
        j = m.end()
    else:  # pagina sem .wrap: logo apos o bloco de estilo
        j = html.index("</style>") + len("</style>")
    html = html[:j] + BARRA + html[j:]

    # 3. a barra de baixo, depois do rodape (ainda dentro do container)
    if "</footer>" in html:
        k = html.rindex("</footer>") + len("</footer>")
        html = html[:k] + BARRA + html[k:]
    else:
        html = html + BARRA

    # 4. o dialogo e o script, no fim do arquivo
    return html + DIALOGO + JS


def main(argv):
    if not argv:
        print(__doc__.strip())
        return 2
    for caminho in argv:
        with open(caminho, encoding="utf-8") as f:
            antes = f.read()
        depois = injetar(antes)
        if depois == antes:
            print(f"  = {caminho} (ja tinha o widget)")
            continue
        with open(caminho, "w", encoding="utf-8") as f:
            f.write(depois)
        print(f"  + {caminho} {len(antes)} -> {len(depois)} bytes")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
