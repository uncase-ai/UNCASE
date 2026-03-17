"""Spanish stopwords, flow step patterns, and text filtering utilities.

Provides a curated set of Spanish function words (articles, prepositions,
conjunctions, pronouns, common verbs, adverbs) that carry no semantic
signal for quality evaluation. Also includes compiled regex patterns for
detecting conversational realizations of expected flow steps across all
supported SCSF domains.
"""

from __future__ import annotations

import re

# ---------------------------------------------------------------------------
# Spanish stopwords (~120 common function words)
# ---------------------------------------------------------------------------

STOPWORDS_ES: frozenset[str] = frozenset(
    {
        # Articles
        "el",
        "la",
        "los",
        "las",
        "un",
        "una",
        "unos",
        "unas",
        # Prepositions
        "de",
        "en",
        "a",
        "por",
        "para",
        "con",
        "sin",
        "sobre",
        "entre",
        "hasta",
        "desde",
        "hacia",
        "bajo",
        "ante",
        "tras",
        "durante",
        "mediante",
        "segun",
        # Conjunctions
        "y",
        "o",
        "pero",
        "sino",
        "que",
        "como",
        "ni",
        "aunque",
        "porque",
        "cuando",
        "donde",
        "mientras",
        "si",
        "pues",
        # Pronouns
        "yo",
        "tu",
        "ella",
        "nosotros",
        "ellos",
        "ellas",
        "me",
        "te",
        "se",
        "lo",
        "le",
        "nos",
        "les",
        "mi",
        "su",
        "sus",
        "mio",
        "tuyo",
        "suyo",
        # Common verbs — ser / estar / haber
        "es",
        "son",
        "ser",
        "soy",
        "somos",
        "fue",
        "era",
        "estar",
        "esta",
        "estan",
        "estoy",
        "estamos",
        "siendo",
        "sido",
        "hay",
        "ha",
        "he",
        "han",
        "hemos",
        # Common verbs — tener / hacer / poder / ir / querer
        "tiene",
        "tengo",
        "tienen",
        "tenemos",
        "hace",
        "hago",
        "hacen",
        "hacemos",
        "puede",
        "puedo",
        "pueden",
        "podemos",
        "va",
        "voy",
        "van",
        "vamos",
        "quiero",
        "quiere",
        "quieren",
        # Common verbs — decir / saber / dar / ver
        "dice",
        "digo",
        "dicen",
        "saber",
        "sabe",
        "sabemos",
        "dar",
        "doy",
        "damos",
        "dan",
        "ver",
        "veo",
        "ven",
        "vemos",
        "ir",
        # Adverbs and other function words
        "no",
        "mas",
        "muy",
        "bien",
        "mal",
        "ya",
        "aqui",
        "ahi",
        "alli",
        "hoy",
        "ahora",
        "tambien",
        "solo",
        "asi",
        "aun",
        # Determiners and quantifiers
        "todo",
        "toda",
        "todos",
        "todas",
        "otro",
        "otra",
        "otros",
        "otras",
        "mismo",
        "cada",
        "este",
        "estos",
        "estas",
        "ese",
        "esa",
        "esos",
        "esas",
        "aquel",
        "mucho",
        "poco",
        "algo",
        "nada",
        "nadie",
        # Relative / interrogative
        "quien",
        "cual",
        "cuyo",
        "cuya",
        "etc",
    }
)

# ---------------------------------------------------------------------------
# Text filtering utilities
# ---------------------------------------------------------------------------

_TOKEN_RE = re.compile(r"\b\w+\b")


def filter_stopwords(tokens: list[str]) -> list[str]:
    """Remove Spanish stopwords from a token list.

    Args:
        tokens: Pre-tokenized words (expected lowercase).

    Returns:
        Filtered list with stopwords removed.
    """
    return [t for t in tokens if t not in STOPWORDS_ES]


def content_tokens(text: str) -> list[str]:
    """Tokenize text, lowercase, and remove stopwords and short words.

    Uses a simple ``\\b\\w+\\b`` tokenizer. Words with 2 characters or fewer
    and Spanish stopwords are discarded.

    Args:
        text: Raw input text.

    Returns:
        List of content-bearing tokens.
    """
    raw = _TOKEN_RE.findall(text.lower())
    return [w for w in raw if len(w) > 2 and w not in STOPWORDS_ES]


def content_token_set(text: str) -> set[str]:
    """Return unique content tokens from text.

    Equivalent to ``set(content_tokens(text))`` but reads slightly better
    at call sites where only uniqueness matters.

    Args:
        text: Raw input text.

    Returns:
        Set of unique content-bearing tokens.
    """
    return set(content_tokens(text))


# ---------------------------------------------------------------------------
# Flow step detection patterns (compiled regexes, IGNORECASE)
# ---------------------------------------------------------------------------

_I = re.IGNORECASE


def _p(*patterns: str) -> list[re.Pattern[str]]:
    """Compile a list of regex patterns with IGNORECASE."""
    return [re.compile(p, _I) for p in patterns]


FLOW_STEP_PATTERNS: dict[str, list[re.Pattern[str]]] = {
    # -- Generic flow steps ------------------------------------------------
    # Greetings
    "saludo": _p(
        r"\b(?:hola|buenos?\s+(?:d[ií]as?|tardes?|noches?))\b",
        r"\bbienvenid[oa]s?\b",
        r"\bmucho\s+gusto\b",
        r"\b(?:saludos|qu[eé]\s+tal)\b",
        r"\bun\s+placer\b",
    ),
    # Needs identification (multiple label variants)
    "identificacion_necesidades": _p(
        r"\bqu[eé]\s+(?:busca|necesita|requiere|le\s+interesa)\b",
        r"\ben\s+qu[eé]\s+(?:puedo|podemos)\s+ayudar\b",
        r"\bcu[aá]les?\s+son\s+sus?\b",
        r"\bpara\s+qu[eé]\b",
        r"\brequisitos?\b",
        r"\bnecesidad(?:es)?\b",
        r"\bqu[eé]\s+tipo\s+de\b",
        r"\bqu[eé]\s+(?:est[aá]\s+buscando|le\s+gustar[ií]a)\b",
    ),
    "consulta_necesidades": _p(
        r"\bqu[eé]\s+(?:busca|necesita|requiere)\b",
        r"\ben\s+qu[eé]\s+(?:puedo|podemos)\s+ayudar\b",
        r"\bcu[eé]nteme\b",
        r"\bqu[eé]\s+(?:problema|situaci[oó]n|motivo)\b",
    ),
    "consulta de necesidades": _p(
        r"\bqu[eé]\s+(?:busca|necesita|requiere)\b",
        r"\ben\s+qu[eé]\s+(?:puedo|podemos)\s+ayudar\b",
        r"\bmotivo\s+de\s+(?:su|la)\s+(?:consulta|visita)\b",
    ),
    "consulta": _p(
        r"\bconsulta\b",
        r"\bpregunta\b",
        r"\bduda\b",
        r"\bqu[eé]\s+(?:necesita|desea|busca)\b",
        r"\ben\s+qu[eé]\s+puedo\b",
    ),
    # Option presentation
    "presentacion_opciones": _p(
        r"\b(?:le\s+(?:presento|muestro|ofrezco)|tenemos|contamos\s+con)\b",
        r"\bopciones?\s+(?:disponibles?|que\s+tenemos)\b",
        r"\balternativas?\b",
        r"\bpuede\s+elegir\b",
        r"\ble\s+recomiendo\b",
        r"\b(?:modelos?|planes?|paquetes?)\s+(?:disponibles?|que)\b",
    ),
    "presentacion de opciones": _p(
        r"\b(?:le\s+(?:presento|muestro)|aqu[ií]\s+tiene)\b",
        r"\bopciones?\b",
        r"\balternativas?\b",
        r"\bcat[aá]logo\b",
    ),
    "presentacion": _p(
        r"\b(?:le\s+presento|permita\s*me|le\s+muestro)\b",
        r"\bpresentar(?:le)?\b",
        r"\bcaracter[ií]sticas?\b",
        r"\bdetall(?:es|ar)\b",
    ),
    # Diagnosis / assessment
    "diagnostico": _p(
        r"\bdiagn[oó]stic[oa]?\b",
        r"\banaliz(?:ar|amos|o)\b",
        r"\brevis(?:ar|i[oó]n|amos)\b",
        r"\b(?:seg[uú]n\s+los\s+)?resultados?\b",
        r"\bexamen(?:es)?\b",
        r"\bestudios?\b",
    ),
    "evaluacion": _p(
        r"\bevalu(?:ar|aci[oó]n|amos)\b",
        r"\bvalorar\b",
        r"\banalizar\b",
        r"\bmedici[oó]n\b",
        r"\binspecci[oó]n\b",
    ),
    "valoracion": _p(
        r"\bvaloraci[oó]n\b",
        r"\bvalorar\b",
        r"\bestimaci[oó]n\b",
        r"\bapreci(?:ar|aci[oó]n)\b",
        r"\bperitaje\b",
    ),
    # Resolution / closing
    "resolucion": _p(
        r"\bresoluci[oó]n\b",
        r"\bresolver\b",
        r"\bsoluci[oó]n(?:ar)?\b",
        r"\bproceder\b",
        r"\bquedamos\s+(?:en|de\s+acuerdo)\b",
        r"\bconclusi[oó]n\b",
    ),
    "cierre": _p(
        r"\bcierre\b",
        r"\bcerrar\b",
        r"\bfirm(?:ar|a)\b",
        r"\bformaliz(?:ar|amos)\b",
        r"\bconfirm(?:ar|amos|ado)\b",
        r"\bacuerdo\s+(?:final|cerrado)\b",
    ),
    "conclusion": _p(
        r"\bconclusi[oó]n\b",
        r"\bconcluir\b",
        r"\bresumen\b",
        r"\ben\s+resumen\b",
        r"\bpara\s+finalizar\b",
        r"\ben\s+conclusi[oó]n\b",
    ),
    # -- Domain-specific steps ---------------------------------------------
    # Automotive
    "financiamiento": _p(
        r"\bfinanciamiento\b",
        r"\bcr[eé]dito\b",
        r"\bmensualidad(?:es)?\b",
        r"\benganche\b",
        r"\bplazos?\b",
        r"\btasa\s+(?:de\s+)?inter[eé]s\b",
        r"\bpr[eé]stamo\b",
        r"\b(?:pago\s+)?inicial\b",
    ),
    "cotizacion": _p(
        r"\bcotizaci[oó]n\b",
        r"\bcotizar\b",
        r"\bprecio\b",
        r"\bcosto\b",
        r"\bpresupuesto\b",
        r"\bcu[aá]nto\s+(?:cuesta|vale|ser[ií]a)\b",
    ),
    "prueba_manejo": _p(
        r"\bprueba\s+(?:de\s+)?manejo\b",
        r"\btest\s+drive\b",
        r"\bprobar\s+(?:el\s+)?(?:auto|veh[ií]culo|carro|coche)\b",
        r"\bmanejo\s+de\s+prueba\b",
    ),
    "seguimiento": _p(
        r"\bseguimiento\b",
        r"\bdar\s+seguimiento\b",
        r"\bcontact(?:ar|o)\s+(?:de\s+)?(?:nuevo|posterior)\b",
        r"\b(?:pr[oó]xima|siguiente)\s+(?:cita|visita|llamada)\b",
        r"\bnos\s+(?:comunicamos|contactamos)\b",
    ),
    # Medical
    "tratamiento": _p(
        r"\btratamiento\b",
        r"\btratar\b",
        r"\bterapia\b",
        r"\bmedic(?:amento|ina|aci[oó]n)\b",
        r"\breceta(?:r)?\b",
        r"\bprescripci[oó]n\b",
        r"\bdosis\b",
        r"\bintervenci[oó]n\b",
    ),
    "recomendacion": _p(
        r"\brecomendaci[oó]n(?:es)?\b",
        r"\brecomendar\b",
        r"\ble\s+(?:sugiero|aconsejo)\b",
        r"\bsugerencia\b",
        r"\bes\s+(?:importante|necesario|conveniente)\s+que\b",
        r"\bindic(?:ar|aciones)\b",
    ),
    # Legal / Finance / Education
    "explicacion": _p(
        r"\bexplic(?:ar|aci[oó]n|o|amos)\b",
        r"\besto\s+(?:significa|quiere\s+decir)\b",
        r"\bes\s+decir\b",
        r"\ben\s+(?:t[eé]rminos|palabras)\s+(?:simples|sencill[oa]s)\b",
        r"\bfundament(?:ar|o|almente)\b",
        r"\bbas[ií]camente\b",
    ),
    "negociacion": _p(
        r"\bnegoci(?:ar|aci[oó]n)\b",
        r"\bcontraoferta\b",
        r"\bcondiciones?\b",
        r"\bterminos?\b",
        r"\bacuerdo\b",
        r"\b(?:mejorar|ajustar)\s+(?:el\s+)?(?:precio|oferta|condiciones)\b",
    ),
    "documentacion": _p(
        r"\bdocumentaci[oó]n\b",
        r"\bdocumentos?\b",
        r"\bpapeleo\b",
        r"\bformulario\b",
        r"\btr[aá]mite\b",
        r"\bcontrato\b",
        r"\bfirm(?:ar|a)\b",
        r"\bidentificaci[oó]n\s+oficial\b",
    ),
    "despedida": _p(
        r"\b(?:hasta\s+(?:luego|pronto|la\s+pr[oó]xima))\b",
        r"\bgracias\s+por\b",
        r"\bbuen\s+(?:d[ií]a|tarde|viaje)\b",
        r"\bnos\s+vemos\b",
        r"\bque\s+(?:le|te)\s+vaya\s+bien\b",
        r"\bfue\s+un\s+(?:placer|gusto)\b",
        r"\bcon\s+(?:gusto|mucho\s+gusto)\b",
    ),
}


def match_flow_step(step_label: str, text: str) -> float:
    """Score how well a text segment realizes a flow step.

    Lookup strategy:
    1. If ``step_label`` (normalized) has entries in ``FLOW_STEP_PATTERNS``,
       attempt regex matching. A hit on any pattern yields **1.0**.
    2. If no pattern matches (or no patterns exist for the label), fall back
       to word-overlap between the label's content words and the text's
       content tokens. An overlap ratio >= 0.5 yields **0.5**.
    3. Otherwise returns **0.0**.

    Args:
        step_label: The flow step label as it appears in ``flujo_esperado``
                    (e.g. ``"saludo"``, ``"identificacion_necesidades"``).
        text: Conversation text to search within.

    Returns:
        ``1.0`` for a strong pattern match, ``0.5`` for partial word
        overlap, ``0.0`` for no match.
    """
    normalized = step_label.strip().lower()

    # 1. Try compiled regex patterns
    patterns = FLOW_STEP_PATTERNS.get(normalized)
    if patterns:
        for pattern in patterns:
            if pattern.search(text):
                return 1.0

    # 2. Fallback: word overlap between label tokens and text tokens
    label_words = content_tokens(normalized.replace("_", " "))
    if not label_words:
        # Label is entirely stopwords / too short — try raw substring
        if normalized.replace("_", " ") in text.lower():
            return 1.0
        return 0.0

    text_tokens = content_token_set(text)
    if not text_tokens:
        return 0.0

    hits = sum(1 for w in label_words if w in text_tokens)
    ratio = hits / len(label_words)

    if ratio >= 0.5:
        return 0.5

    return 0.0
