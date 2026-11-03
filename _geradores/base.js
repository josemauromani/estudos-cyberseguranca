/**
 * ============================================================================
 * ESTUDOS DE CIBERSEGURANÇA — BIBLIOTECA BASE COMPARTILHADA (base.js)
 * Utilitários, persistência local segura e comportamento do chassi (sumário, leitura,
 * checklist, questões, conclusão, gaveta).
 * Vanilla JavaScript (Zero dependências externas, 100% offline-ready).
 * ============================================================================
 */

(function (window, document) {
  'use strict';

  // --------------------------------------------------------------------------
  // 0. Utilitários Seguros de Armazenamento Local (localStorage)
  // --------------------------------------------------------------------------
  function safeStorageGet(key) {
    try {
      if (typeof window !== 'undefined' && window.localStorage) {
        return window.localStorage.getItem(key);
      }
    } catch (e) {
      console.warn(`[CS] Falha ao ler localStorage chave "${key}":`, e);
    }
    return null;
  }

  function safeStorageSet(key, value) {
    try {
      if (typeof window !== 'undefined' && window.localStorage) {
        window.localStorage.setItem(key, String(value));
        return true;
      }
    } catch (e) {
      console.warn(`[CS] Falha ao gravar localStorage chave "${key}":`, e);
    }
    return false;
  }

  // --------------------------------------------------------------------------
  // 1. Gerenciamento de Tema (Claro / Escuro)
  // --------------------------------------------------------------------------
  const THEME_STORAGE_KEY = 'cs_theme';

  function applyTheme(theme) {
    if (theme === 'dark') {
      document.documentElement.setAttribute('data-theme', 'dark');
    } else if (theme === 'light') {
      document.documentElement.setAttribute('data-theme', 'light');
    } else {
      document.documentElement.removeAttribute('data-theme');
    }
    updateThemeButtons(theme);
  }

  function getSystemTheme() {
    return window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches
      ? 'dark'
      : 'light';
  }

  function getCurrentTheme() {
    const saved = safeStorageGet(THEME_STORAGE_KEY);
    return saved || getSystemTheme();
  }

  function updateThemeButtons(currentTheme) {
    const effectiveTheme = currentTheme === 'dark' || (!currentTheme && getSystemTheme() === 'dark') ? 'dark' : 'light';
    const buttons = document.querySelectorAll('.theme-toggle-btn, [data-theme-toggle]');
    buttons.forEach((btn) => {
      btn.setAttribute('aria-label', effectiveTheme === 'dark' ? 'Alternar para tema claro' : 'Alternar para tema escuro');
      btn.innerHTML = effectiveTheme === 'dark'
        ? '<span class="theme-icon">☀️</span> <span class="theme-label">Claro</span>'
        : '<span class="theme-icon">🌙</span> <span class="theme-label">Escuro</span>';
    });
  }

  function toggleTheme() {
    const current = getCurrentTheme();
    const next = current === 'dark' ? 'light' : 'dark';
    safeStorageSet(THEME_STORAGE_KEY, next);
    applyTheme(next);
    return next;
  }

  function initTheme() {
    const saved = safeStorageGet(THEME_STORAGE_KEY);
    if (saved) {
      applyTheme(saved);
    } else {
      updateThemeButtons(getSystemTheme());
    }

    // Monitora preferência do sistema operacional caso usuário não tenha fixado
    if (window.matchMedia) {
      window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
        if (!safeStorageGet(THEME_STORAGE_KEY)) {
          updateThemeButtons(e.matches ? 'dark' : 'light');
        }
      });
    }

    // Vincula cliques em botões de tema
    document.querySelectorAll('.theme-toggle-btn, [data-theme-toggle]').forEach((btn) => {
      btn.onclick = toggleTheme;
    });
  }

  // --------------------------------------------------------------------------
  // 2. Slug, chaves de armazenamento e utilitários do chassi
  // --------------------------------------------------------------------------
  function extractSlug() {
    if (document.body && document.body.dataset && document.body.dataset.slug) {
      return document.body.dataset.slug;
    }
    const metaSlug = document.querySelector('meta[name="study-slug"]');
    if (metaSlug && metaSlug.content) {
      return metaSlug.content;
    }
    // Fallback: tenta obter do pathname
    const match = window.location.pathname.match(/treinamento-([^.]+)\.html/);
    if (match) {
      return match[1];
    }
    return 'default';
  }

  const TIPOS = {
    teoria: { icone: '📘', rotulo: 'Teoria' },
    laboratorio: { icone: '🧪', rotulo: 'Laboratório' },
    checklist: { icone: '☑️', rotulo: 'Checklist' },
    questoes: { icone: '❓', rotulo: 'Questões de concurso' },
    referencias: { icone: '📚', rotulo: 'Referências' },
  };

  function lerJson(chave, padrao) {
    const bruto = safeStorageGet(chave);
    if (bruto === null) return padrao;
    try {
      const valor = JSON.parse(bruto);
      return valor === null || valor === undefined ? padrao : valor;
    } catch (e) {
      return padrao;
    }
  }

  function secoes() {
    return Array.from(document.querySelectorAll('section.study-section'));
  }

  function itemDoSumario(id) {
    if (!id) return null;
    return document.querySelector('a.toc-item[href="#' + id + '"]');
  }

  function definirContador(secao, texto) {
    if (!secao) return;
    const item = itemDoSumario(secao.id);
    const contador = item ? item.querySelector('.toc-contador') : null;
    if (contador) contador.textContent = texto;
  }

  function secaoDoTipo(tipo) {
    return document.querySelector('section.study-section[data-tipo="' + tipo + '"]');
  }

  // --------------------------------------------------------------------------
  // 3. Checklist Operacional Interativo & Status de Conclusão de Estudo
  // --------------------------------------------------------------------------
  const SELETOR_ITEM_CHECKLIST = '.checklist-item, .check-item';

  function updateChecklistProgress(checklistEl) {
    const checkboxes = checklistEl.querySelectorAll('input[type="checkbox"]');
    if (!checkboxes.length) return;

    let checkedCount = 0;
    checkboxes.forEach((cb) => {
      if (cb.checked) checkedCount++;
    });
    const pct = Math.round((checkedCount / checkboxes.length) * 100);

    // Cabeçalho "N de M" (chassi novo): o texto é o rótulo; a barra lê --progresso.
    const head = checklistEl.previousElementSibling;
    if (head && head.classList.contains('checklist-head')) {
      head.textContent = `${checkedCount} de ${checkboxes.length}`;
      head.style.setProperty('--progresso', `${pct}%`);
    }

    // Barra e contador do checklist legado (Fundamentos-Ciber).
    const progressFill = checklistEl.querySelector('.checklist-progress-fill');
    if (progressFill) {
      progressFill.style.width = `${pct}%`;
    }
    const counterEl = checklistEl.querySelector('.checklist-counter');
    if (counterEl) {
      counterEl.textContent = `${checkedCount} de ${checkboxes.length} itens auditados`;
    }
  }

  function atualizarContadoresChecklist() {
    document.querySelectorAll('section.study-section[data-tipo="checklist"]').forEach((secao) => {
      const caixas = secao.querySelectorAll('.checklist input[type="checkbox"]');
      if (!caixas.length) return;
      let marcados = 0;
      caixas.forEach((cb) => {
        if (cb.checked) marcados++;
      });
      definirContador(secao, `${marcados}/${caixas.length}`);
    });
  }

  function initChecklist(slug) {
    // O slug canônico é o de body[data-slug]; o argumento só vale como reserva
    // para páginas sem ele (módulos antigos chamavam initChecklist("<slug-kebab>")).
    const comDataSlug = document.body && document.body.dataset && document.body.dataset.slug;
    const activeSlug = comDataSlug ? comDataSlug : (slug || extractSlug());
    const checklists = document.querySelectorAll('.checklist');

    checklists.forEach((checklist, listIdx) => {
      const listId = checklist.dataset.checklistId || `list_${listIdx}`;
      const items = checklist.querySelectorAll(SELETOR_ITEM_CHECKLIST);

      // Cabeçalho "N de M" antes de cada lista (idempotente).
      if (checklist.tagName === 'UL' && items.length) {
        const anterior = checklist.previousElementSibling;
        if (!anterior || !anterior.classList.contains('checklist-head')) {
          const head = document.createElement('div');
          head.className = 'checklist-head';
          checklist.parentNode.insertBefore(head, checklist);
        }
      }

      items.forEach((item, itemIdx) => {
        const checkbox = item.querySelector('input[type="checkbox"]');
        if (!checkbox) return;

        const itemId = checkbox.id || checkbox.getAttribute('data-id') || `${listId}_${itemIdx}`;
        const storageKey = `cs_check_${activeSlug}_${itemId}`;

        // Restaura estado
        const savedState = safeStorageGet(storageKey);
        if (savedState === 'true') {
          checkbox.checked = true;
          item.classList.add('completed');
        } else {
          checkbox.checked = false;
          item.classList.remove('completed');
        }

        // Event listener
        checkbox.onchange = function () {
          safeStorageSet(storageKey, checkbox.checked ? 'true' : 'false');
          if (checkbox.checked) {
            item.classList.add('completed');
          } else {
            item.classList.remove('completed');
          }
          updateChecklistProgress(checklist);
          atualizarContadoresChecklist();
        };
      });

      updateChecklistProgress(checklist);
    });
    atualizarContadoresChecklist();
  }

  function isStudyDone(slug) {
    const activeSlug = slug || extractSlug();
    return safeStorageGet(`cs_done_${activeSlug}`) === 'true';
  }

  function setStudyDone(slug, isDone) {
    const activeSlug = slug || extractSlug();
    const doneValue = isDone !== false;
    return safeStorageSet(`cs_done_${activeSlug}`, doneValue ? 'true' : 'false');
  }

  // --------------------------------------------------------------------------
  // 4. Questões: flashcards com autoavaliação e múltipla escolha
  // --------------------------------------------------------------------------
  const RESULTADOS = ['acertei', 'errei', 'revisar'];

  function quizId(quizItem) {
    if (quizItem.dataset.q) return quizItem.dataset.q;
    if (quizItem.dataset.quizId) return quizItem.dataset.quizId;
    return `quiz_${Array.from(document.querySelectorAll('.quiz-item')).indexOf(quizItem)}`;
  }

  function quizKey(quizItem) {
    return `cs_quiz_${extractSlug()}_${quizId(quizItem)}`;
  }

  let filtroQuiz = 'todas';

  function aplicarFiltroQuiz() {
    document.querySelectorAll('.quiz-item').forEach((q) => {
      const v = q.dataset.res;
      let mostrar = true;
      if (filtroQuiz === 'pendentes') mostrar = v === 'errei' || v === 'revisar';
      if (filtroQuiz === 'sem') mostrar = !v;
      q.hidden = !mostrar;
    });
  }

  function atualizarPlacar() {
    const itens = Array.from(document.querySelectorAll('.quiz-item'));
    const n = { acertei: 0, errei: 0, revisar: 0 };
    itens.forEach((q) => {
      if (n[q.dataset.res] !== undefined) n[q.dataset.res]++;
    });
    const placar = document.querySelector('.quiz-score');
    if (placar) {
      RESULTADOS.forEach((r) => {
        const el = placar.querySelector(`[data-n="${r}"]`);
        if (el) el.textContent = String(n[r]);
      });
    }
    const secao = secaoDoTipo('questoes') || (itens[0] && itens[0].closest('section.study-section'));
    definirContador(secao, `${n.acertei}/${itens.length}`);
  }

  function marcarBotoesAutoavaliacao(quizItem) {
    quizItem.querySelectorAll('.quiz-selfeval button').forEach((b) => {
      const ativo = b.dataset.v === quizItem.dataset.res;
      b.classList.toggle('on', ativo);
      b.setAttribute('aria-pressed', ativo ? 'true' : 'false');
    });
  }

  function definirResultado(quizItem, valor, persistir) {
    if (RESULTADOS.indexOf(valor) === -1) return;
    quizItem.dataset.res = valor;
    if (persistir) safeStorageSet(quizKey(quizItem), valor);
    marcarBotoesAutoavaliacao(quizItem);
    atualizarPlacar();
    aplicarFiltroQuiz();
  }

  function garantirAutoavaliacao(details) {
    const quizItem = details.closest('.quiz-item');
    if (!quizItem || !details.open) return;
    if (!details.querySelector('.quiz-selfeval')) {
      const bloco = document.createElement('div');
      bloco.className = 'quiz-selfeval';
      bloco.innerHTML =
        '<span>Como você foi?</span>' +
        '<button type="button" data-v="acertei">✓ Acertei</button>' +
        '<button type="button" data-v="errei">✗ Errei</button>' +
        '<button type="button" data-v="revisar">↻ Revisar depois</button>';
      bloco.querySelectorAll('button').forEach((b) => {
        b.addEventListener('click', () => definirResultado(quizItem, b.dataset.v, true));
      });
      details.appendChild(bloco);
    }
    marcarBotoesAutoavaliacao(quizItem);
  }

  function criarPlacar(primeiroItem) {
    if (document.querySelector('.quiz-score')) return;
    const secao = primeiroItem.closest('section.study-section');
    let ancora = primeiroItem;
    while (secao && ancora.parentNode && ancora.parentNode !== secao) ancora = ancora.parentNode;
    const placar = document.createElement('div');
    placar.className = 'quiz-score';
    placar.innerHTML =
      '<span>✓ Acertei <b data-n="acertei">0</b></span>' +
      '<span>✗ Errei <b data-n="errei">0</b></span>' +
      '<span>↻ Revisar <b data-n="revisar">0</b></span>' +
      '<div class="quiz-filtros" role="group" aria-label="Filtrar questões">' +
      '<button type="button" class="on" aria-pressed="true" data-f="todas">Todas</button>' +
      '<button type="button" aria-pressed="false" data-f="pendentes">Erradas e a revisar</button>' +
      '<button type="button" aria-pressed="false" data-f="sem">Sem resposta</button></div>';
    placar.querySelectorAll('.quiz-filtros button').forEach((b) => {
      b.addEventListener('click', () => {
        filtroQuiz = b.dataset.f;
        placar.querySelectorAll('.quiz-filtros button').forEach((x) => {
          x.classList.toggle('on', x === b);
          x.setAttribute('aria-pressed', x === b ? 'true' : 'false');
        });
        aplicarFiltroQuiz();
      });
    });
    ancora.parentNode.insertBefore(placar, ancora);
  }

  function checkQuiz(btn, isCorrect, explanation) {
    const quizItem = btn.closest('.quiz-item');
    if (!quizItem) return;

    // Desabilita botões para registrar a tentativa
    const buttons = quizItem.querySelectorAll('.quiz-btn');
    buttons.forEach((b) => {
      b.disabled = true;
      b.classList.remove('selected');
    });

    // Destaca o botão clicado
    btn.classList.add('selected');
    if (isCorrect) {
      btn.classList.add('correct');
    } else {
      btn.classList.add('incorrect');
    }

    // Exibe ou atualiza o painel de feedback
    let feedbackEl = quizItem.querySelector('.quiz-feedback');
    if (!feedbackEl) {
      feedbackEl = document.createElement('div');
      feedbackEl.className = 'quiz-feedback';
      quizItem.appendChild(feedbackEl);
    }

    feedbackEl.className = `quiz-feedback ${isCorrect ? 'correct' : 'incorrect'}`;
    const icon = isCorrect ? '✅' : '❌';
    const statusText = isCorrect ? 'Correto!' : 'Incorreto.';
    feedbackEl.innerHTML = `<strong>${icon} ${statusText}</strong> ${escapeHtml(explanation || '')}`;
    feedbackEl.style.display = 'block';

    // O primeiro clique conta no placar (acertei/errei); tentativas seguintes não mudam o resultado.
    if (!quizItem.dataset.res) {
      definirResultado(quizItem, isCorrect ? 'acertei' : 'errei', true);
    }
  }

  function initQuiz() {
    const quizItems = Array.from(document.querySelectorAll('.quiz-item'));
    if (!quizItems.length) return;

    criarPlacar(quizItems[0]);

    quizItems.forEach((quiz) => {
      quiz.setAttribute('data-initialized', 'true');
      const salvo = safeStorageGet(quizKey(quiz));
      if (RESULTADOS.indexOf(salvo) !== -1) quiz.dataset.res = salvo;

      quiz.querySelectorAll('details.quiz-details').forEach((details) => {
        details.addEventListener('toggle', () => garantirAutoavaliacao(details));
        garantirAutoavaliacao(details);
      });
      marcarBotoesAutoavaliacao(quiz);
    });

    atualizarPlacar();
    aplicarFiltroQuiz();
  }

  // --------------------------------------------------------------------------
  // 5. Copiar Código para Área de Transferência
  // --------------------------------------------------------------------------
  function copyCode(button, targetId) {
    let textToCopy = '';

    if (targetId) {
      const targetEl = document.getElementById(targetId);
      if (targetEl) {
        textToCopy = targetEl.innerText || targetEl.textContent;
      }
    } else if (button) {
      const terminalBox = button.closest('.terminal-box') || button.parentElement;
      const codeEl = terminalBox ? terminalBox.querySelector('pre code, pre, code') : null;
      if (codeEl) {
        textToCopy = codeEl.innerText || codeEl.textContent;
      }
    }

    if (!textToCopy) return;

    const originalText = button ? button.innerText : 'Copiar';

    function setSuccess() {
      if (button) {
        button.innerText = '✓ Copiado!';
        button.classList.add('copied');
        setTimeout(() => {
          button.innerText = originalText;
          button.classList.remove('copied');
        }, 2000);
      }
    }

    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(textToCopy.trim()).then(setSuccess).catch(() => {
        fallbackCopy(textToCopy.trim(), setSuccess);
      });
    } else {
      fallbackCopy(textToCopy.trim(), setSuccess);
    }
  }

  function fallbackCopy(text, callback) {
    if (!document.body) {
      console.warn('document.body não está pronto para cópia via textarea.');
      return;
    }

    const textarea = document.createElement('textarea');
    textarea.value = text;
    textarea.style.position = 'fixed';
    textarea.style.opacity = '0';
    document.body.appendChild(textarea);
    textarea.select();
    try {
      const successful = document.execCommand('copy');
      if (successful && callback) {
        callback();
      }
    } catch (e) {
      console.warn('Falha ao copiar texto:', e);
    } finally {
      if (textarea.parentNode) {
        textarea.parentNode.removeChild(textarea);
      }
    }
  }

  // --------------------------------------------------------------------------
  // 5b. Utilitários Reutilizáveis para Simuladores e Laboratórios
  // --------------------------------------------------------------------------
  function escapeHtml(str) {
    if (str === null || str === undefined) return '';
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }

  function formatBytes(bytes, decimals = 2) {
    if (!+bytes || bytes < 0) return '0 Bytes';
    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return `${parseFloat((bytes / Math.pow(k, i)).toFixed(dm))} ${sizes[i]}`;
  }

  function formatNumber(num) {
    if (isNaN(num)) return '0';
    return new Intl.NumberFormat('pt-BR').format(num);
  }

  function bytesToHex(uint8Array) {
    return Array.from(uint8Array)
      .map((b) => b.toString(16).padStart(2, '0'))
      .join('');
  }

  function hexToBytes(hexString) {
    let cleaned = String(hexString || '').replace(/\s+/g, '');
    if (cleaned.length % 2 !== 0) {
      cleaned = '0' + cleaned;
    }
    const bytes = new Uint8Array(cleaned.length / 2);
    for (let i = 0; i < cleaned.length; i += 2) {
      bytes[i / 2] = parseInt(cleaned.substring(i, i + 2), 16);
    }
    return bytes;
  }

  async function sha256Hex(message) {
    if (!window.crypto || !window.crypto.subtle) {
      throw new Error('Web Cryptography API não suportada neste ambiente.');
    }
    const msgUint8 = new TextEncoder().encode(message);
    const hashBuffer = await window.crypto.subtle.digest('SHA-256', msgUint8);
    const hashArray = Array.from(new Uint8Array(hashBuffer));
    return hashArray.map((b) => b.toString(16).padStart(2, '0')).join('');
  }

  // --------------------------------------------------------------------------
  // 6. Sumário, leitura, conclusão, último acesso e gaveta
  // --------------------------------------------------------------------------
  const estado = { lidas: new Set(), vistas: new Set(), atual: null, ultimaGravada: null };

  function atualizarSumario() {
    const lista = secoes();
    if (!lista.length) return;
    const alt = window.innerHeight;
    const doc = document.documentElement;

    // Seção atual: a última cujo topo passou de 35% da janela.
    let atual = lista[0];
    lista.forEach((s) => {
      if (s.getBoundingClientRect().top < alt * 0.35) atual = s;
    });
    // Uma seção só conta como lida se já foi a atual em algum momento (um salto pelo
    // sumário não marca as puladas) e se seu fim passou de 60% da janela.
    estado.vistas.add(atual.id);
    lista.forEach((s) => {
      if (estado.vistas.has(s.id) && s.getBoundingClientRect().bottom < alt * 0.6) estado.lidas.add(s.id);
    });
    if (window.scrollY + alt >= doc.scrollHeight - 4) {
      // Fim da página: só a seção atual e a última (que pode ser curta demais para virar "atual").
      estado.lidas.add(atual.id);
      estado.lidas.add(lista[lista.length - 1].id);
    }

    // Barra de leitura no topo
    const rolavel = doc.scrollHeight - alt;
    const pctRolagem = rolavel > 0 ? Math.min(100, Math.max(0, (window.scrollY / rolavel) * 100)) : 0;
    const barra = document.querySelector('.readbar');
    if (barra) barra.style.setProperty('--progresso', `${pctRolagem.toFixed(1)}%`);

    // Itens do sumário
    lista.forEach((s) => {
      const item = itemDoSumario(s.id);
      if (!item) return;
      const ehAtual = s === atual;
      item.classList.toggle('on', ehAtual);
      item.classList.toggle('lida', estado.lidas.has(s.id) && !ehAtual);
      if (ehAtual) item.setAttribute('aria-current', 'true');
      else item.removeAttribute('aria-current');
    });

    // Selo do tipo atual
    const tipo = TIPOS[atual.dataset.tipo];
    const selo = document.querySelector('.tipo-atual');
    if (selo && tipo) {
      selo.textContent = `${tipo.icone} ${tipo.rotulo}`;
      selo.style.setProperty('--c', `var(--tipo-${atual.dataset.tipo})`);
    }

    // Percentual lido
    const pct = Math.round((lista.filter((s) => estado.lidas.has(s.id)).length / lista.length) * 100);
    const prog = document.querySelector('.toc-progresso');
    if (prog) {
      prog.textContent = `${pct}%`;
      prog.style.setProperty('--progresso', `${pct}%`);
    }
    atualizarBotaoConcluir(pct);

    // Persistência: leitura e último acesso
    const lidasOrdenadas = lista.filter((s) => estado.lidas.has(s.id)).map((s) => s.id);
    const chaveLeitura = `cs_read_${extractSlug()}`;
    const salva = lerJson(chaveLeitura, []);
    if (JSON.stringify(salva) !== JSON.stringify(lidasOrdenadas)) {
      safeStorageSet(chaveLeitura, JSON.stringify(lidasOrdenadas));
    }
    estado.atual = atual.id;
    if (estado.ultimaGravada !== atual.id) {
      estado.ultimaGravada = atual.id;
      safeStorageSet('cs_last', JSON.stringify({ slug: extractSlug(), secao: atual.id, ts: Date.now() }));
    }
  }

  function atualizarBotaoConcluir(pct) {
    const concluido = isStudyDone();
    const total = secoes().length;
    const percentual = pct === undefined
      ? Math.round((secoes().filter((s) => estado.lidas.has(s.id)).length / (total || 1)) * 100)
      : pct;
    document.querySelectorAll('.btn-concluir').forEach((b) => {
      b.classList.toggle('concluido', concluido);
      b.classList.toggle('pronto', !concluido && percentual === 100);
      b.setAttribute('aria-pressed', concluido ? 'true' : 'false');
      b.textContent = concluido ? '✓ Concluído · desfazer' : '✓ Concluir módulo';
    });
  }

  function initLeitura() {
    const lista = secoes();
    if (!lista.length) return;
    const ids = new Set(lista.map((s) => s.id));
    const salvas = lerJson(`cs_read_${extractSlug()}`, []);
    if (Array.isArray(salvas)) {
      salvas.forEach((id) => {
        if (typeof id === 'string' && ids.has(id)) estado.lidas.add(id);
      });
    }
    window.addEventListener('scroll', atualizarSumario, { passive: true });
    window.addEventListener('resize', atualizarSumario);
    window.addEventListener('load', atualizarSumario);
    atualizarSumario();
  }

  function initConcluir() {
    document.querySelectorAll('.btn-concluir').forEach((b) => {
      b.addEventListener('click', () => {
        setStudyDone(extractSlug(), !isStudyDone());
        atualizarBotaoConcluir();
      });
    });
    atualizarBotaoConcluir();
  }

  function initGaveta() {
    const botao = document.querySelector('.toc-toggle');
    const body = document.body;
    if (!botao) return;

    function definir(aberta, devolverFoco) {
      body.classList.toggle('toc-aberto', aberta);
      botao.setAttribute('aria-expanded', aberta ? 'true' : 'false');
      if (!aberta && devolverFoco) botao.focus();
    }

    botao.addEventListener('click', () => definir(!body.classList.contains('toc-aberto'), true));
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && body.classList.contains('toc-aberto')) definir(false, true);
    });
    // O overlay (body::before) cobre a página inteira: um clique fora do sumário fecha.
    document.addEventListener('click', (e) => {
      if (!body.classList.contains('toc-aberto')) return;
      if (e.target.closest && (e.target.closest('.toc') || e.target.closest('.toc-toggle'))) return;
      definir(false, true);
    });
    document.querySelectorAll('a.toc-item').forEach((item) => {
      item.addEventListener('click', () => {
        if (!body.classList.contains('toc-aberto')) return;
        definir(false, false);
        // A navegação por âncora tira o foco do elemento ativo; devolve depois dela.
        setTimeout(() => botao.focus(), 0);
      });
    });
  }

  // Um simulador pode informar o progresso do laboratório ao sumário (opcional).
  function labProgress(feitos, total) {
    const secao = secaoDoTipo('laboratorio');
    const f = Number(feitos);
    const t = Number(total);
    if (!Number.isFinite(f) || !Number.isFinite(t) || t <= 0) {
      definirContador(secao, '');
      return;
    }
    definirContador(secao, `${Math.max(0, Math.min(f, t))}/${t}`);
  }

  // --------------------------------------------------------------------------
  // 6b. Glossário: tooltip dos termos (<dfn class="glossario">)
  // --------------------------------------------------------------------------
  function initGlossario() {
    const fonte = document.getElementById('glossario-dados');
    if (!fonte) return;
    let dados;
    try {
      dados = JSON.parse(fonte.textContent);
    } catch (e) {
      return;
    }
    const termos = Array.from(document.querySelectorAll('dfn.glossario[data-termo]'));
    if (!termos.length) return;
    termos.forEach((t) => t.removeAttribute('title'));

    const pop = document.createElement('div');
    pop.id = 'glossario-pop';
    pop.className = 'glossario-pop';
    pop.setAttribute('role', 'tooltip');
    pop.hidden = true;
    document.body.appendChild(pop);

    let atual = null;
    let timer = null;
    const MARGEM = 16;

    function limpaTimer() {
      if (timer) {
        clearTimeout(timer);
        timer = null;
      }
    }

    function posicionar() {
      if (!atual) return;
      // Zera a posição antes de medir: left/top antigos encolhem a largura do popover.
      pop.style.left = '0';
      pop.style.top = '0';
      const r = atual.getBoundingClientRect();
      const w = pop.offsetWidth;
      const h = pop.offsetHeight;
      const maxEsq = Math.max(MARGEM, window.innerWidth - MARGEM - w);
      const esq = Math.min(Math.max(r.left, MARGEM), maxEsq);
      let topo = r.bottom + 6;
      if (topo + h > window.innerHeight - 8 && r.top - 6 - h >= 0) topo = r.top - 6 - h;
      pop.style.left = esq + 'px';
      pop.style.top = Math.max(0, topo) + 'px';
    }

    function abrir(termo) {
      limpaTimer();
      const v = dados[termo.getAttribute('data-termo')];
      if (!v) return;
      if (atual && atual !== termo) atual.removeAttribute('aria-describedby');
      atual = termo;
      const id = termo.getAttribute('data-termo');
      pop.textContent = '';
      const titulo = document.createElement('div');
      titulo.className = 'glossario-pop-titulo';
      titulo.textContent = v.categoria ? v.termo + ' · ' + v.categoria : v.termo;
      pop.appendChild(titulo);
      const sub = v.sigla_de || v.termo_ingles;
      if (sub) {
        const el = document.createElement('div');
        el.className = 'glossario-pop-sub';
        el.textContent = sub;
        pop.appendChild(el);
      }
      const texto = document.createElement('div');
      texto.className = 'glossario-pop-texto';
      texto.innerHTML = v.significado || '';
      pop.appendChild(texto);
      const link = document.createElement('a');
      link.className = 'glossario-pop-link';
      link.href = '../index.html#v-glossario/' + id;
      link.textContent = 'Ver no glossário →';
      pop.appendChild(link);
      pop.hidden = false;
      termo.setAttribute('aria-describedby', 'glossario-pop');
      posicionar();
    }

    function fechar() {
      limpaTimer();
      pop.hidden = true;
      if (atual) atual.removeAttribute('aria-describedby');
      atual = null;
    }

    function agendarFechar() {
      limpaTimer();
      timer = setTimeout(fechar, 200);
    }

    function dentro(el) {
      return !!el && ((atual && atual.contains(el)) || pop.contains(el));
    }

    termos.forEach((t) => {
      t.addEventListener('mouseenter', () => {
        limpaTimer();
        timer = setTimeout(() => abrir(t), 150);
      });
      t.addEventListener('mouseleave', agendarFechar);
      t.addEventListener('focus', () => abrir(t));
      t.addEventListener('click', () => {
        if (atual !== t) abrir(t);
      });
      t.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && atual === t) {
          fechar();
          t.focus();
        } else if (e.key === 'Tab' && !e.shiftKey && atual === t) {
          const link = pop.querySelector('a.glossario-pop-link');
          if (link) {
            e.preventDefault();
            link.focus();
          }
        }
      });
      t.addEventListener('focusout', (e) => {
        if (!dentro(e.relatedTarget)) agendarFechar();
      });
    });

    pop.addEventListener('mouseenter', limpaTimer);
    pop.addEventListener('mouseleave', agendarFechar);
    pop.addEventListener('focusin', limpaTimer);
    pop.addEventListener('focusout', (e) => {
      if (!dentro(e.relatedTarget)) agendarFechar();
    });
    pop.addEventListener('keydown', (e) => {
      if (!atual) return;
      if (e.key === 'Tab' && e.shiftKey) {
        e.preventDefault();
        atual.focus();
      } else if (e.key === 'Escape') {
        const t = atual;
        fechar();
        t.focus();
      }
    });
    document.addEventListener('click', (e) => {
      if (atual && !dentro(e.target)) fechar();
    });
    window.addEventListener('resize', posicionar);
    window.addEventListener('scroll', posicionar, { passive: true });
  }

  let iniciado = false;
  function init() {
    if (iniciado) return;
    iniciado = true;
    initTheme();
    initChecklist();
    initQuiz();
    initConcluir();
    initGaveta();
    initLeitura();
    initGlossario();
  }

  // --------------------------------------------------------------------------
  // 7. Exposição Global de Funções & Inicialização Automática
  // --------------------------------------------------------------------------
  window.safeStorageGet = safeStorageGet;
  window.safeStorageSet = safeStorageSet;
  window.initTheme = initTheme;
  window.toggleTheme = toggleTheme;
  window.initChecklist = initChecklist;
  window.isStudyDone = isStudyDone;
  window.setStudyDone = setStudyDone;
  window.initQuiz = initQuiz;
  window.checkQuiz = checkQuiz;
  window.copyCode = copyCode;
  window.escapeHtml = escapeHtml;
  window.formatBytes = formatBytes;
  window.formatNumber = formatNumber;
  window.bytesToHex = bytesToHex;
  window.hexToBytes = hexToBytes;
  window.sha256Hex = sha256Hex;

  // Namespace unificado
  window.CS = {
    init,
    initGlossario,
    labProgress,
    safeStorageGet,
    safeStorageSet,
    initTheme,
    toggleTheme,
    initChecklist,
    isStudyDone,
    setStudyDone,
    initQuiz,
    checkQuiz,
    copyCode,
    escapeHtml,
    formatBytes,
    formatNumber,
    bytesToHex,
    hexToBytes,
    sha256Hex,
  };

  // Auto-inicialização na carga do DOM
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})(window, document);
