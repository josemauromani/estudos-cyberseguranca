# Glossário com tooltip nos módulos — design

**Data:** 2026-11-03
**Status:** Aprovada e implementada
**Tamanho:** subsistema novo (dados, marcação no build, tooltip nos módulos e visão nova no portal); sem módulo novo.

## Intenção

Siglas e termos técnicos aparecem em vários módulos sem uma explicação comum. O estudante que encontra "HMAC" no Estudo 01 precisa de três coisas: o significado ali mesmo, sem sair da página; uma explicação mais longa com o histórico da sigla ou da palavra (quem criou, quando, em que norma); e saber em que outros módulos o termo aparece. O glossário resolve isso com um cadastro único de verbetes, um tooltip automático nos módulos e uma visão nova no portal.

## Objetivos

1. Cadastro único de verbetes em `_geradores/glossario_dados.py`, com o primeiro verbete: **HMAC**.
2. Marcação automática no build: todo módulo que cita um termo cadastrado ganha o tooltip, sem editar o corpo do módulo.
3. Tooltip acessível nos módulos (mouse, teclado e toque), com link para o verbete no portal.
4. Visão **📖 Glossário** no menu lateral do portal, com busca, índice por letra e a lista de módulos onde cada termo aparece.

## Não objetivos

- Escrever outros verbetes além do HMAC.
- Modo híbrido para forçar ou bloquear a marcação num trecho do corpo. Fica para depois, se aparecer falso positivo.
- Página de glossário separada do portal.
- Tooltip dentro do JavaScript dos laboratórios, de botões do quiz ou de itens do checklist.

## Decisões tomadas com o usuário

| Pergunta | Decisão |
|---|---|
| Como um termo vira tooltip | Marcação **automática no build**. Não há custo de token: é um passo determinístico em Python, sem IA |
| Onde fica o glossário | **Nova visão no portal** (`index.html`) |
| Campos do verbete | Todos os propostos, mais **termo em inglês** |
| Implementação | Verbetes em Python + marcação por `html.parser` + popover próprio no `base.js` |
| Alcance do HMAC | Tooltip nos módulos que citam HMAC (6 na conversa; 5 na implementação, porque Active-Directory-Fundamentos só cita `RC4-HMAC`, que a regra de fronteira não casa); a validação manual é feita no Estudo 01 |

## Abordagens consideradas

| Abordagem | Troca | Decisão |
|---|---|---|
| 1. Verbetes em Python + marcação por parser HTML + popover próprio | Zero dependências e no padrão do `index_dados.py`; o parser nunca marca dentro de atributo, código ou script. Texto longo fica numa string Python | **Escolhida** |
| 2. Um arquivo Markdown por verbete com cabeçalho de campos | Mais confortável para texto longo, mas exige um mini-parser próprio (YAML traria dependência) | Descartada |
| 3. Regex no HTML bruto + atributo `title` | Mais simples, mas frágil (marca dentro de atributos e do JS do laboratório); `title` não funciona no toque, não aceita link e não é acessível | Descartada |

## O que muda

### 1. Dados: `_geradores/glossario_dados.py`

Uma lista `GLOSSARIO` de dicionários, um por verbete.

| Campo | Obrigatório | Tipo | Uso |
|---|---|---|---|
| `id` | sim | `str`, `^[a-z0-9]+(-[a-z0-9]+)*$` | âncora e URL (`#v-glossario/<id>`) |
| `termo` | sim | `str` | forma exibida e casada no texto |
| `significado` | sim | `str`, 1 a 3 frases | tooltip e verbete |
| `sigla_de` | não | `str` | forma por extenso (inglês + tradução entre parênteses) |
| `termo_ingles` | não | `str` | para palavras em português (ex.: Integridade → *Integrity*) |
| `categoria` | não | `str` | etiqueta do verbete |
| `explicacao` | não | `str` | texto longo, só no portal |
| `historico` | não | `str` | origem, autores, ano, normas |
| `variacoes` | não | `list[str]` | outras formas casadas no texto |
| `relacionados` | não | `list[str]` | ids de outros verbetes |
| `referencias` | não | `list[tuple[str, str]]` | (rótulo, URL) |

Campos de texto aceitam apenas `<strong>`, `<em>` e `<code>` como HTML inline. "Aparece em" não é campo: o build calcula.

Verbete inicial:

- **id:** `hmac`
- **termo:** HMAC
- **sigla_de:** Hash-based Message Authentication Code (Código de Autenticação de Mensagem baseado em Hash)
- **categoria:** Criptografia
- **significado:** código que combina uma função de hash (ex.: SHA-256) com uma chave secreta compartilhada. Prova a integridade e a autenticidade da mensagem: quem não tem a chave não consegue recalcular o valor.
- **explicacao:** diferença para um hash simples (que qualquer um recalcula depois de alterar a mensagem); onde é usado (TLS, IPsec, JWT com HS256, HOTP/TOTP, assinatura de webhooks); o que não oferece: não-repúdio, porque as duas partes têm a mesma chave. Para não-repúdio, assinatura digital com chave assimétrica.
- **historico:** proposto por Mihir Bellare, Ran Canetti e Hugo Krawczyk em 1996, no artigo "Keying Hash Functions for Message Authentication" (CRYPTO '96). Publicado como RFC 2104 em fevereiro de 1997 e padronizado pelo NIST no FIPS 198 (2002), revisado no FIPS 198-1 (2008).
- **variacoes:** HMAC-SHA256, HMAC-SHA1
- **relacionados:** nenhum (os verbetes de Hash, SHA-256, Assinatura digital e JWT ainda não existem; entram quando forem cadastrados)
- **referencias:** RFC 2104 (`https://www.rfc-editor.org/rfc/rfc2104`), FIPS 198-1 (`https://csrc.nist.gov/pubs/fips/198-1/final`)

### 2. Marcação no build: `_geradores/glossario.py`

Função pública:

```python
marcar_termos(html: str, verbetes: list[dict]) -> tuple[str, list[str]]
```

Devolve o HTML marcado e a lista ordenada de ids usados.

- Percorre o corpo com `html.parser.HTMLParser` da biblioteca padrão e só altera **nós de texto**. Tags e atributos saem byte a byte como entraram.
- **Contextos ignorados** (nada dentro deles é marcado): `pre`, `code`, `kbd`, `samp`, `script`, `style`, `svg`, `textarea`, `h1` a `h6`, `a`, `button`, `label`, `dfn`, qualquer elemento com classe `terminal-box` ou `mermaid`.
- **Sigla x palavra:** o termo (ou variação) sem nenhuma letra minúscula é sigla e casa diferenciando maiúsculas de minúsculas. Os demais casam sem diferenciar.
- **Fronteira:** o caractere antes e o depois do trecho casado não podem ser letra (inclusive acentuada), dígito, `_` nem `-`. Assim "HMAC-SHA256" não vira "HMAC" + "-SHA256", e "HMACs" não casa.
- **Variações:** contam como o mesmo verbete. Quando duas formas casam no mesmo ponto, vence a mais longa. O texto exibido é o original do corpo.
- **Densidade:** só a 1ª ocorrência de cada verbete **por seção** (`section.study-section`). Texto fora de seção não é marcado.
- **Saída:** `<dfn class="glossario" data-termo="hmac" tabindex="0" title="<significado sem HTML>">HMAC</dfn>`. O `title` é o fallback para quem está sem JavaScript; o `base.js` o remove ao iniciar, para não duplicar com o popover.

Integração no `montar.py`, na função `montar_treinamento`:

1. Depois de `validar_corpo` e de `extrair_secoes`, antes de `processar_diagramas_html`: `body_content, ids = marcar_termos(body_content, GLOSSARIO)`.
2. Se `ids` não estiver vazio, a página recebe antes do `<script>` do `base.js` um `<script type="application/json" id="glossario-dados">` com apenas os verbetes usados, cada um com `id`, `termo`, `categoria`, `sigla_de`, `termo_ingles` e `significado`. Os caracteres `<`, `>` e `&` são escapados como `<`, `>` e `&`. Módulo sem termos não recebe o bloco.

Resultado esperado no Estudo 01 (`fundamentos_ciber_body.html`): HMAC marcado no texto corrido das seções de teoria (linhas 46, 114 e 207 hoje, uma vez por seção). Ficam sem marca o botão do quiz (linhas 406–407, dentro de `button`) e o texto do laboratório (linha 729, dentro de `script`).

### 3. Tooltip no módulo: `base.js` e `base.css`

`initGlossario()` no `base.js`, chamada na inicialização do chassi:

- Lê `#glossario-dados`. Se não existir, não faz nada.
- Cria **um** popover (`div.glossario-pop`, `role="tooltip"`, `id="glossario-pop"`) no `body` e o reaproveita para todos os termos.
- Conteúdo: linha "HMAC · Criptografia"; linha com `sigla_de` ou `termo_ingles` (se houver); o significado; o link **Ver no glossário →** para `../index.html#v-glossario/<id>`.
- **Mouse:** abre ao passar sobre o termo, depois de 150 ms. Continua aberto enquanto o cursor estiver no termo ou no popover. Fecha 200 ms depois de sair dos dois.
- **Teclado:** abre no `focus` do termo. `Esc` fecha e devolve o foco ao termo. O link do popover é alcançável com Tab logo depois do termo.
- **Toque:** o 1º toque abre (sem seguir link algum). Tocar fora fecha.
- **Posição:** abaixo do termo. Se não couber até a borda inferior da janela, acima. Nunca ultrapassa as bordas laterais (respeita 16 px de margem na largura de celular).
- Enquanto aberto, o termo tem `aria-describedby="glossario-pop"`. Ao fechar, o atributo sai.

`base.css`, numa seção "Glossário":

- `dfn.glossario`: sem itálico, sublinhado pontilhado, cursor de ajuda, contorno de foco visível.
- `.glossario-pop`: cartão com largura máxima de 22 rem, cores só por variáveis de `tokens.css`, funcionando nos temas claro e escuro.

### 4. Visão "Glossário" no portal: `build_index.py` e `index.css`

- `VISOES` ganha `("glossario", "📖", "Glossário")` depois de `("progresso", ...)`. O link do menu mostra a contagem de verbetes.
- `render_glossario(verbetes, aparece_em, status_map)` gera `<section class="view" data-view="glossario" hidden>` com:
  - campo de busca;
  - índice de letras A–Z, ativas apenas as que têm verbete;
  - grupos por letra inicial, em ordem alfabética que ignora acentos e maiúsculas;
  - um `<article class="verbete" id="g-<id>">` por verbete, com todos os campos preenchidos, nesta ordem: termo e categoria, sigla_de, termo_ingles, Significado, Explicação, Histórico, Variações, Relacionados, Referências e Aparece em. Campo vazio não aparece.
- **Relacionados:** link para `#v-glossario/<id>` do outro verbete. Id inexistente faz o build falhar com mensagem clara.
- **Referências:** links externos com `target="_blank" rel="noopener"`.
- **Aparece em:** o `build_index.py` roda `marcar_termos` sobre o corpo de cada módulo e junta os ids encontrados. Os chips reaproveitam `render_chip_modulo`, com o status de progresso, na ordem do catálogo.
- **Roteamento:** `visaoDoHash()` passa a aceitar `#v-<visao>/<ancora>`. Para `#v-glossario/hmac`: mostra a visão, rola até `#g-hmac` e aplica a classe `destaque` no cartão por 2 s. Id desconhecido mostra a visão no topo.
- **Busca:** filtra no navegador por termo, sigla_de, termo_ingles, variações e significado, ignorando acentos e maiúsculas. Grupos de letra sem resultado somem. Sem resultado: mensagem "Nenhum termo encontrado".
- Estilos em `index.css`, só com variáveis de token.

### 5. Documentação

- `_geradores/GUIA-DO-AUTOR.md`: seção "Glossário", com como cadastrar um verbete, as regras de marcação (contextos ignorados, sigla x palavra, fronteira, 1ª ocorrência por seção) e quando um termo deve entrar no glossário.
- `README.md`: o portal passa de seis para **sete visões**, com a descrição do Glossário.

### 6. Entrega

`base.js` e `base.css` mudam, então os 60 módulos e o portal são recompilados com `./_geradores/gerar.sh todos`. O commit de build fica separado dos commits de código, como no restante do repositório. Módulos que citam HMAC hoje e passam a ter tooltip: Fundamentos-Ciber, Criptografia-Pratica, Autenticacao-e-IAM, Seguranca-em-APIs e SOAR-e-Automacao-de-Resposta. Active-Directory-Fundamentos só cita `RC4-HMAC` (tipo de criptografia do Kerberos), que a regra de fronteira não casa, e fica sem tooltip.

## Testes

Seguem o padrão `unittest` do projeto e rodam só os arquivos afetados (conferir `free -h` antes).

- `testes/test_glossario_dados.py`: campos obrigatórios presentes; ids únicos e no formato; `relacionados` apontam para ids existentes; referências com URL `https://`; campos de texto sem HTML fora de `<strong>`, `<em>` e `<code>`.
- `testes/test_glossario.py`, unidade de `marcar_termos`:
  - marca a 1ª ocorrência por seção e de novo na seção seguinte;
  - não marca dentro de cada contexto ignorado nem em valor de atributo;
  - sigla diferencia maiúsculas e minúsculas; palavra não;
  - fronteira: "HMAC-SHA256", "HMACs" e "XHMAC" não casam como HMAC;
  - variação mais longa vence;
  - remover as tags `dfn` do resultado devolve exatamente o HTML de entrada.
- Módulo compilado: o Estudo 01 contém `dfn.glossario[data-termo="hmac"]` e `#glossario-dados` com só o HMAC; um módulo sem termos não contém `#glossario-dados`.
- Portal: a visão `glossario` existe; o menu tem o link com a contagem; `#g-hmac` lista os 5 módulos.
- Navegador (harness `testes/navegador.py`, Chrome headless):
  - módulo: foco no termo abre o popover com o significado; `Esc` fecha; o link aponta para `../index.html#v-glossario/hmac`; sem erros no console;
  - portal: abrir `#v-glossario/hmac` mostra a visão e o cartão `#g-hmac`; a busca por "autenticacao" encontra o HMAC e por "xyz" mostra a mensagem de vazio.
- Testes existentes que contam ou listam as visões do menu passam a esperar sete.
- `test_compilados_atualizados.py` continua passando após `gerar.sh todos`.

## Riscos

- **Falso positivo na marcação** (uma palavra comum cadastrada como verbete marcando trechos que não são o termo técnico). Mitigação: 1ª ocorrência por seção e contextos ignorados; o modo híbrido fica como evolução.
- **Divergência entre "Aparece em" e o módulo compilado.** Mitigação: os dois usam a mesma função `marcar_termos` sobre o mesmo corpo.
