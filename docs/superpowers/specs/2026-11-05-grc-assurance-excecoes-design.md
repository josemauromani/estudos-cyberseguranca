# Design Spec: Aprimoramentos de GRC — Exceções, Security Assurance, CIS Controls e CGEIT

**Data:** 2026-11-05
**Status:** Aprovada pelo usuário (2026-11-05)
**Repositório:** `estudos_cyberseguranca` (Mapa da Cibersegurança)
**Referência Metodológica:** Superpowers Spec-Driven Development (SDD)

---

## 1. Propósito e Entendimento

A análise do catálogo frente a uma vaga de **Especialista em Governança, Risco e Compliance (GRC) de TI** mostrou que o Mapa já cobre com força a maior parte dos requisitos (Auditoria/SOX/ITGC/COBIT no 58, ISO 27001/27002 no 26, Riscos de TI no 25, Terceiros no 57, Três Linhas e comunicação executiva no 59/60, nuvem no 21/53, certificações CISA/CRISC/CISSP/CCSP/ISO 27001 LA no 33). Restaram poucas lacunas específicas que a vaga nomeia. Esta spec fecha cinco delas, **todas como seções ou edições de módulos existentes** — sem módulo novo; o catálogo segue em **62 módulos**.

### Estado atual (2026-11-05)

- **Módulo 25 (Gestao-de-Riscos-TI):** seções Introdução; ISO 31000/Matriz 5×5; ISO/IEC 27005:2022; Laboratório; Checklist; Questões; Fatos. Títulos numerados no texto do `<h2>`.
- **Módulo 58 (Auditoria-de-TI):** Introdução; SOX 404/ICFR; ITGC/ITAC/SOC 1; COBIT 2019; O Ciclo do Teste (walkthrough→remediação); Laboratório (Testador de ITGC); Checklist; Questões; Fatos. Títulos numerados.
- **Módulo 26 (ISO-27001-e-27002):** Introdução; **"SGSI, Anexo A, CIS Controls e NIST SP 800-53"** (já cita CIS Controls); Laboratório (SoA); Checklist; Questões; Fatos. Títulos numerados.
- **Módulo 33 (Certificacoes-e-Carreira):** matriz de **17** certificações em `CERTIFICACOES` (`index_dados.py`) e no JSON `#cert-dados`. CISA, CISM, CRISC, CDPSE presentes; **CGEIT ausente** (0 ocorrências no repo).
- "Exceção de segurança"/"gestão de exceções": **0 ocorrências**. "Security Assurance"/efetividade de controle: só tangenciado no 58.
- Padrão do Mapa: cada módulo tem teoria, laboratório, checklist, questões e referências; callouts sempre com modificador; conteúdo em pt-BR; nenhuma ferramenta de fornecedor recomendada.
- Numeração dos `<h2>` é do autor (ex.: "2. …"); inserir seção exige renumerar os títulos seguintes (mecânico).

### Decisões do usuário

| Decisão | Escolha |
|---|---|
| Itens | Todos os 5 da análise de GRC |
| Item 2 (Security Assurance) | **Seção no módulo 58** (não módulo novo) |
| Forma das adições | Seção de teoria **+ 1–2 questões** cada (fiel ao padrão), não teoria enxuta |

### Critérios de sucesso

- Catálogo permanece em **62 módulos**; nenhum módulo muda de número ou trilha.
- Os 5 itens entram nos módulos 25, 26, 33 e 58 conforme a tabela da §3.
- Cada módulo editado continua passando em `contrato.validar_corpo`, compila com `montar.py`/`gerar.sh` e passa no seu teste (`test_gestao_riscos_ti`, `test_auditoria_de_ti`, `test_iso_27001_27002`, `test_certificacoes_carreira`).
- A matriz e o planejador mostram **18** certificações; CGEIT tem ao menos 3 módulos e coerência `CERTIFICACOES` ↔ `#cert-dados`.
- Suíte `unittest` inteira passa (teto de memória do CLAUDE.md); `gerar.sh todos` compila sem erro.
- `test_marca` segue verde (nenhum nome antigo/autor).

### Não objetivos

- Módulo novo, mudança de numeração ou de trilha.
- Recomendar/endossar uma ferramenta de GRC específica (ServiceNow/Archer/MetricStream entram só como exemplos de categoria).
- Simuladores novos (as adições são seções de teoria; os módulos já têm seu laboratório).
- Reescrever os módulos de destino.

### Anti-objetivos (falha mesmo funcionando)

- Item 4 duplicar os CIS **Benchmarks** do Hardening (06): o foco é distinguir os 18 **Controls** (o que fazer) dos Benchmarks (como endurecer).
- Item 2 repetir o teste de controle do "Ciclo do Teste" já existente no 58: a seção nova trata **desenho × efetividade**, racionalização e o **modelo de assurance**, remetendo ao ciclo existente.
- Item 1 repetir o cálculo de risco do 25: a exceção parte do risco já calculado e trata a **aceitação formal** dele.
- Inventar domínios, pesos ou anos de experiência da **CGEIT**: vêm da página oficial da ISACA ou o texto diz "confira na página oficial" (padrão `requisitos: {"conferir": true}` como CISA/CISM).
- Nomear fornecedor de GRC como recomendação, ou apresentar correlação sistêmica como ferramenta mágica.

---

## 2. Abordagens Consideradas

| Abordagem | Troca | Decisão |
|---|---|---|
| **A. Tudo como seções/edições em módulos existentes** | Barato, catálogo em 62, aproveita módulos fortes de GRC; cada módulo cresce um pouco | **Escolhida** |
| B. Item 2 como módulo novo (63) "Security Assurance" | Mais profundidade e laboratório próprio, mas catálogo a 63, simulador, testes e documentação; custo alto | Descartada pelo usuário |
| C. Item 4 como seção nova no 26 | Redundante — o 26 já tem seção que cita CIS Controls; melhor expandir | Descartada |

---

## 3. Itens, Lares e Conteúdo

| Item | Módulo | Forma |
|---|---|---|
| 1. Exceções de segurança | 25 (Riscos de TI) | seção de teoria nova |
| 2. Security Assurance e efetividade de controles | 58 (Auditoria de TI) | seção de teoria nova |
| 5. Correlação sistêmica + automação de GRC | 58 (Auditoria de TI) | seção de teoria nova |
| 4. CIS Controls (18 + Implementation Groups) | 26 (ISO) | expandir a seção existente (subseção `h3`) |
| 3. CGEIT | 33 (Certificações) | matriz 17 → 18 |

Cada adição de seção segue o contrato do corpo (`GUIA-DO-AUTOR.md` §2): `<section class="study-section" id=… data-tipo="teoria">` com `<h2>`, callouts com modificador, tabelas `data-table`, e **1–2 questões** acrescentadas à seção de questões existente do módulo, mais referência(s) oficial(is) na seção de referências. (Nos módulos 25/26/58 os `<h2>` não são numerados no texto — ver §3.6 —, então não há renumeração.)

### 3.1 Item 1 — Exceções de segurança (módulo 25)

Seção nova após "ISO/IEC 27005:2022", antes do laboratório. Conteúdo:
- A exceção como **aceitação formal e temporária de risco** quando um controle/requisito não pode ser cumprido agora (parte do risco já tratado no módulo).
- **Ciclo:** solicitação (quem pede, qual controle não é cumprido, por quê) → análise do risco → **aprovação por alçada** (quanto maior o risco, mais alto o aprovador) → **controle compensatório** → **prazo e plano de remediação** → **reavaliação/expiração** (exceção não é permanente).
- **Como a função de GRC desafia uma exceção:** a justificativa é técnica ou conveniência? o compensatório existe de fato? o prazo é realista? o **acúmulo** de exceções vira risco sistêmico (liga ao item 5)?
- Tabela: estados da exceção (solicitada, aprovada, vigente, vencida, encerrada) e papéis.
- Callout `warning`: exceção vencida é risco aceito sem dono — a auditoria (58) procura exatamente isso.
- Remissões: 26 (SoA/controles), 58 (auditoria de exceções). 1–2 questões + referência (ISO/IEC 27001 tratamento de risco; NIST SP 800-37 risk acceptance).

### 3.2 Item 2 — Security Assurance e efetividade de controles (módulo 58)

Seção nova após "COBIT 2019" / "O Ciclo do Teste". Conteúdo:
- **Desenho × efetividade operacional:** um controle pode estar bem desenhado e ainda assim falhar na operação; assurance cobre os dois.
- **Tipos de teste e força da evidência:** indagação < observação < inspeção < reexecução; por que indagação sozinha é fraca (remete ao Ciclo do Teste existente, sem repeti-lo).
- **Modelo de assurance:** escopo, critérios, ritos/cadência, indicadores, evidências e **governança de planos de ação**.
- **Racionalização de controles:** mapear controle→risco para cortar redundância e cobrir risco material (um controle que cobre vários riscos vs. dez que cobrem o mesmo).
- Onde o assurance se encaixa nas **Três Linhas** (remete ao 59).
- Tabela: desenho vs efetividade; tabela dos tipos de teste e evidência.
- Remissões: 59 (três linhas), 25 (risco e exceções), 26 (controles). 1–2 questões + referências (IIA/COSO, ISACA ITAF).

### 3.3 Item 5 — Correlação sistêmica e automação de GRC (módulo 58)

Seção nova após a do item 2. Conteúdo:
- **Causas sistêmicas:** achados isolados escondem a raiz; juntar apontamentos de auditoria + incidentes + vulnerabilidades + exceções + riscos revela o problema de fundo (ex.: o mesmo controle de acesso falho em 3 auditorias, 2 incidentes e 5 exceções = problema sistêmico de IAM, não 10 achados).
- **O que uma plataforma de GRC (IRM) automatiza:** registro único de riscos/controles/achados, workflow de planos de ação, mapeamento controle↔risco↔requisito, indicadores — **por conceito**; ServiceNow GRC, Archer e MetricStream citados só como exemplos da categoria, sem recomendação.
- Callout `tip`: a função transversal de GRC conecta sinais dispersos; a ferramenta ajuda, mas não substitui o julgamento.
- Remissões: 25 (riscos), 09 (vulnerabilidades), 46/47 (detecção/hunting como fonte de sinal), 18 (incidentes). 1–2 questões + referência (ISACA/IRM; OCEG GRC Capability Model se confirmável).

### 3.4 Item 4 — CIS Controls vs Benchmarks (módulo 26, acréscimo mínimo)

**Correção do builder check:** o módulo 26 **já cobre** os 18 CIS Controls v8.1, os Implementation Groups (IG1/IG2/IG3) e o crosswalk ISO↔CIS↔NIST (as subseções "CIS Controls v8.1 e NIST SP 800-53 Rev. 5" e "Crosswalk" já existem na seção `sgsi`). O crosswalk está travado em **15 entradas** por `test_crosswalk_tem_15_entradas_completas` — **não mexer** nele. O único ponto genuinamente ausente é a **distinção entre CIS Controls e CIS Benchmarks**.

Escopo do item 4, portanto, **mínimo**: acrescentar à seção `sgsi` um parágrafo (ou callout) que distingue **CIS Controls** (os 18 — "o que fazer", já listados ali) dos **CIS Benchmarks** (endurecimento por dispositivo, módulo 06 — "como configurar"), mais **1 questão nova** na seção de questões do 26. Sem nova subseção de tabela, sem re-listar os 18, sem tocar no crosswalk. Referência: CIS Controls v8.1.

### 3.5 Item 3 — CGEIT na matriz (módulo 33)

- `CERTIFICACOES` (`index_dados.py`): nova entrada no padrão de CRISC/CDPSE — `sigla` "CGEIT", `site_oficial` da ISACA, `nome` "Certified in the Governance of Enterprise IT", `orgao` "ISACA", `foco` "Governança de TI corporativa", `experiencia` conferida na ISACA (ou texto "confira"), `modulos`: `["Lideranca-e-Programa-de-Seguranca", "Estruturacao-da-Area-de-Seguranca", "Auditoria-de-TI", "Gestao-de-Riscos-TI", "ISO-27001-e-27002"]`.
- `#cert-dados` no corpo do 33: entrada correspondente com domínios da **CGEIT** (da página oficial da ISACA; se um domínio não tiver módulo, `parcial` + nota, como no padrão) e `requisitos: {"conferir": true}` (como CISA/CISM). Entrada no bloco de lookup `slug→{numero,titulo}` se existir.
- CGEIT entra **sem pesos** (como CEH/GSEC): domínios reais da ISACA com `peso: None`, módulos mapeados, `nota` onde um domínio não tiver módulo; `requisitos: {"conferir": true}`. **Não** adicionar CGEIT aos conjuntos `com_pesos`/`esperados`/`test_revisao_contra_fontes_oficiais`.
- Matriz passa de **17 para 18**. Ripple de testes e textos a ajustar (ver §3.6).

### 3.6 Ripple de testes e textos (do builder check — os testes são contrato editável, não congelado)

A §3.5 original só citava `test_certificacoes_carreira.py`. O builder check mapeou o alcance real; o plano precisa de tarefas explícitas para:

- **Módulo 25 (item 1):** `test_gestao_riscos_ti.py` fixa `iso-27005` imediatamente antes do laboratório e "Seção 7 de 7". Inserir a seção de exceções **entre** a `iso-27005` e o laboratório quebra a asserção de adjacência e a contagem → atualizar o teste para a nova ordem e "Seção 8 de 8".
- **Módulo 58 (itens 2 e 5):** `test_auditoria_de_ti.py::test_secoes` fixa uma lista de **9 ids** e "Seção N de 9". Duas seções novas → lista de **11 ids** e "Seção N de 11"; inserir os ids novos na posição certa.
- **Módulo 33 (item 3, CGEIT):** além de `test_certificacoes_carreira.py`, ajustar:
  - `test_rota_vaga.py` — a lista ordenada de **17 siglas** e o dict `DOMINIO_OFICIAL` (CGEIT → isaca.org);
  - o parágrafo do planejador no corpo do 33 e a lista "requisito… só em texto" do `CURRICULO.md` (ambos cobrados por `test_textos_listam_todas_as_certificacoes_conferir`, já que CGEIT terá `requisitos.conferir=True`);
  - o subtítulo do módulo 33 e as duas ocorrências de "17 certificações" no `README.md` → 18.
- Qualquer outro teste/helper que itere `CERTIFICACOES` e trave contagem/ordem.

**Nota:** os `<h2>` dos módulos 25, 26 e 58 **não** são numerados no texto (o chassi gera "Seção 0X"), então **não há** renumeração de título a fazer nesses módulos (diferente do módulo 01). A tarefa de renumeração citada antes era vazia e sai.

---

## 4. Ordem de Entrega (sugerida ao plano)

1. Item 3 (CGEIT) — menor e isolado.
2. Item 4 (CIS Controls vs Benchmarks) — acréscimo mínimo no 26.
3. Item 1 (exceções) — módulo 25.
4. Itens 2 e 5 — módulo 58 (duas seções correlatas).
5. `gerar.sh todos`, suíte completa, varredura de nome.

## 5. O que fica com o builder

- Redação final em pt-BR e o texto exato das questões, dentro do que cada subseção define.
- Confirmar nas fontes oficiais os dados citados (domínios/experiência da CGEIT na ISACA; cláusulas ISO/NIST). Onde a fonte não publicar, usar "confira na página oficial".
- Posição exata de inserção das seções novas (sem renumerar `<h2>` nos módulos 25/26/58).
