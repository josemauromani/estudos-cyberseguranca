/**
 * ============================================================================
 * ESTUDOS DE CIBERSEGURANÇA — BIBLIOTECA BASE COMPARTILHADA (base.js)
 * Utilitários reativos, persistência local segura, acessibilidade e interatividade.
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
  // 2. Checklist Operacional Interativo & Status de Conclusão de Estudo
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

  function updateChecklistProgress(checklistEl) {
    const checkboxes = checklistEl.querySelectorAll('input[type="checkbox"]');
    if (!checkboxes.length) return;

    let checkedCount = 0;
    checkboxes.forEach((cb) => {
      if (cb.checked) checkedCount++;
    });

    const progressFill = checklistEl.querySelector('.checklist-progress-fill');
    if (progressFill) {
      const pct = Math.round((checkedCount / checkboxes.length) * 100);
      progressFill.style.width = `${pct}%`;
    }

    const counterEl = checklistEl.querySelector('.checklist-counter');
    if (counterEl) {
      counterEl.textContent = `${checkedCount} de ${checkboxes.length} itens auditados`;
    }
  }

  function initChecklist(slug) {
    const activeSlug = slug || extractSlug();
    const checklists = document.querySelectorAll('.checklist');

    checklists.forEach((checklist, listIdx) => {
      const listId = checklist.dataset.checklistId || `list_${listIdx}`;
      const items = checklist.querySelectorAll('.check-item');

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
        };
      });

      updateChecklistProgress(checklist);
    });
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
  // 3. Sistema de Quiz com Feedback Explicativo
  // --------------------------------------------------------------------------
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
  }

  function initQuiz() {
    const quizItems = document.querySelectorAll('.quiz-item');
    quizItems.forEach((quiz, idx) => {
      const qId = quiz.dataset.quizId || `quiz_${idx}`;
      quiz.setAttribute('data-initialized', 'true');
    });
  }

  // --------------------------------------------------------------------------
  // 4. Copiar Código para Área de Transferência
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
  // 5. Utilitários Reutilizáveis para Simuladores e Laboratórios
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
  // 6. Exposição Global de Funções & Inicialização Automática
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
    document.addEventListener('DOMContentLoaded', () => {
      initTheme();
      initChecklist();
      initQuiz();
    });
  } else {
    initTheme();
    initChecklist();
    initQuiz();
  }
})(window, document);
