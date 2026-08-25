from __future__ import annotations

import re
from dataclasses import asdict, dataclass


@dataclass(frozen=True, slots=True)
class OperatorMatch:
    key: str
    lexeme: str
    start: int
    end: int
    role: str

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


# The exact lexeme is retained. The canonical key is only an index into the
# source grammar and never replaces the note occurrence.
_PATTERNS: list[tuple[str, str, str]] = [
    ("ZERO_INFINITY", r"0\s*(?:↔|<->|⇄|–|-)?\s*(?:∞|inf(?:inity)?)", "reciprocal closure reading"),
    ("R_I", r"\br\s*(?:↔|<->|⇄)\s*i\b", "extension/rotation reading"),
    ("TRIANGLE_TIME", r"\bi\s*=\s*2\s*\^\s*\(?\s*r\s*-\s*1\s*\)?", "Triangle Time"),
    ("SHELL_RETURN", r"S_?\(?k\s*\+\s*1\)?\s*=\s*S_?k\s*-\s*2\s*\^\s*\(?S_?\(?k\s*\+\s*1\)?\s*-\s*1\)?", "implicit shell return"),
    ("CHAITIN_KAKEYA", r"\bCK\s*=\s*i\s*e\s*\^\s*K\b", "Chaitin–Kakeya rule/direction"),
    ("K_ORDER", r"K_?n\s*=\s*P_?i\s*\^\s*n\s*\(?P_?i\s*-\s*1\)?\s*\^\s*n", "directional ordering"),
    ("TAN_SEAM", r"tan\s*\(\s*(?:π|pi)\s*/\s*2\s*\)", "rotation–extension inter-bound fold"),
    ("PREDUAL_FOURIER", r"σ\s*\(\s*l_r\s*,\s*g_r\s*,\s*l_i\s*,\s*g_i\s*\)\s*=\s*\(\s*g_i\s*,\s*l_i\s*,\s*g_r\s*,\s*l_r\s*\)", "predual Fourier exchange"),
    ("FOUR_I", r"1\s*(?:→|->)\s*i\s*(?:→|->)\s*-1\s*(?:→|->)\s*-i\s*(?:→|->)\s*1", "four-i return"),
    ("POINT_LINE_LOOP", r"point\s*(?:→|->)\s*line\s*(?:→|->)\s*loop\s*(?:→|->)\s*(?:return|closure)\s*(?:→|->)\s*(?:new\s+)?point", "point–line–loop–return"),
    ("BALL_TIME", r"point\s*(?:→|->)\s*circle\s*(?:→|->)\s*sphere\s*(?:→|->)\s*filled\s+sphere\s*(?:→|->)\s*point", "ball-time return"),
    ("BALL_HAIR", r"ball\s*(?:↔|<->|⇄)\s*hair", "ball/hair reciprocal reading"),
    ("LOOP_SENSOR_SELECTION", r"loop\s*(?:↔|<->|⇄)\s*sensor(?:\s*(?:↔|<->|⇄)\s*selection)?", "loop/sensor/selection continuity"),
    ("SENSOR_SELECTION", r"sensor\s*(?:↔|<->|⇄)\s*selection", "sensor/selection continuity"),
    ("HALT_CONTINUATION", r"halt(?:ing)?\s*(?:↔|<->|⇄)\s*continu(?:ation|ing)", "local halt/reopening reading"),
    ("PROOF_ASSUMPTION", r"(?:proof\s*(?:↔|<->|⇄)\s*assumption|assumption\s*(?:↔|<->|⇄)\s*proof)", "proof/assumption continuity"),
    ("PARTITION_CURVATURE", r"partition\s*(?:↔|<->|⇄)\s*unitary\s+curvature", "partition/unitary-curvature reading"),
    ("METAVECTORIZATION", r"\bmeta\s*-?\s*vector(?:ization|isation|s)?\b|\bmetavector(?:ization|isation|s)?\b", "metavectorization"),
]

_COMPILED = [(key, re.compile(pattern, re.IGNORECASE), role) for key, pattern, role in _PATTERNS]
_TOKEN = re.compile(r"[\w∞πσΔηθκ]+", re.UNICODE)


def extract_operator_path(text: str) -> list[dict[str, object]]:
    matches: list[OperatorMatch] = []
    for key, pattern, role in _COMPILED:
        for match in pattern.finditer(text):
            matches.append(OperatorMatch(key, match.group(0), match.start(), match.end(), role))
    matches.sort(key=lambda item: (item.start, item.end, item.key))
    return [item.as_dict() for item in matches]


def extract_exact_symbols(text: str, path: list[dict[str, object]] | None = None) -> list[str]:
    path = path if path is not None else extract_operator_path(text)
    symbols: list[str] = []
    for item in path:
        lexeme = str(item["lexeme"])
        if lexeme not in symbols:
            symbols.append(lexeme)
    return symbols


def semantic_tokens(text: str) -> set[str]:
    return {token.casefold() for token in _TOKEN.findall(text) if len(token) > 1}


def jaccard(left: str, right: str) -> float:
    a, b = semantic_tokens(left), semantic_tokens(right)
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def operator_keys(path: list[dict[str, object]]) -> list[str]:
    return [str(item["key"]) for item in path]
