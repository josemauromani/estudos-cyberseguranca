# -*- coding: utf-8 -*-
"""
Cadastro de verbetes do glossário — Estudos em Cibersegurança
=============================================================
Um dicionário por verbete. Campos de texto aceitam apenas <strong>, <em>
e <code> como HTML inline. A validação fica em glossario.py.
"""

from typing import Any, Dict, List

GLOSSARIO: List[Dict[str, Any]] = [
    {
        "id": "hmac",
        "termo": "HMAC",
        "sigla_de": "Hash-based Message Authentication Code (Código de Autenticação de Mensagem baseado em Hash)",
        "categoria": "Criptografia",
        "significado": (
            "Código que combina uma função de hash (ex.: SHA-256) com uma chave secreta compartilhada. "
            "Prova a integridade e a autenticidade da mensagem: quem não tem a chave não consegue "
            "recalcular o valor."
        ),
        "explicacao": (
            "Um hash simples pode ser recalculado por qualquer pessoa depois de alterar a mensagem; o HMAC "
            "não, porque o cálculo depende da chave secreta. É usado em TLS, IPsec, JWT com <code>HS256</code>, "
            "HOTP/TOTP e na assinatura de webhooks. O que o HMAC não oferece é não-repúdio, porque as duas "
            "partes têm a mesma chave. Para não-repúdio, use assinatura digital com chave assimétrica."
        ),
        "historico": (
            "Proposto por Mihir Bellare, Ran Canetti e Hugo Krawczyk em 1996, no artigo "
            "<em>Keying Hash Functions for Message Authentication</em> (CRYPTO '96). Publicado como "
            "RFC 2104 em fevereiro de 1997 e padronizado pelo NIST no FIPS 198 (2002), revisado no "
            "FIPS 198-1 (2008)."
        ),
        "variacoes": ["HMAC-SHA256", "HMAC-SHA1"],
        "relacionados": [],
        "referencias": [
            ("RFC 2104", "https://www.rfc-editor.org/rfc/rfc2104"),
            ("FIPS 198-1", "https://csrc.nist.gov/pubs/fips/198-1/final"),
        ],
    },
]
