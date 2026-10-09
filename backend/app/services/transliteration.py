import re
import jellyfish
from rapidfuzz import fuzz

VOWELS_SIGNS = {'ा', 'ि', 'ी', 'ु', 'ू', 'े', 'ै', 'ो', 'ौ', 'ं', '्'}

CONSONANTS_MAP = {
    'क': 'k', 'ख': 'kh', 'ग': 'g', 'घ': 'gh', 'ङ': 'ng',
    'च': 'ch', 'छ': 'chh', 'ज': 'j', 'झ': 'jh', 'ञ': 'ny',
    'ट': 't', 'ठ': 'th', 'ड': 'd', 'ढ': 'dh', 'ण': 'n',
    'त': 't', 'थ': 'th', 'द': 'd', 'ध': 'dh', 'न': 'n',
    'प': 'p', 'फ': 'ph', 'ब': 'b', 'भ': 'bh', 'म': 'm',
    'य': 'y', 'र': 'r', 'ल': 'l', 'व': 'v', 'श': 'sh', 'ष': 'sh', 'स': 's', 'ह': 'h',
    'ळ': 'l', 'क्ष': 'ksh', 'ज्ञ': 'dny',
}

INDEPENDENT_VOWELS = {
    'अ': 'a', 'आ': 'aa', 'इ': 'i', 'ई': 'ee', 'उ': 'u', 'ऊ': 'oo', 'ऋ': 'ri',
    'ए': 'e', 'ऐ': 'ai', 'ओ': 'o', 'औ': 'au', 'अं': 'an', 'अः': 'ah',
}

MATRAS_MAP = {
    'ा': 'a', 'ि': 'i', 'ी': 'i', 'ु': 'u', 'ू': 'u', 'े': 'e', 'ै': 'ai', 'ो': 'o', 'ौ': 'au', 'ं': 'n', '्': ''
}

def devanagari_to_latin(text: str) -> str:
    if not text:
        return ""
    result = []
    length = len(text)
    for i, char in enumerate(text):
        if char in INDEPENDENT_VOWELS:
            result.append(INDEPENDENT_VOWELS[char])
        elif char in CONSONANTS_MAP:
            base_l = CONSONANTS_MAP[char]
            next_char = text[i+1] if i + 1 < length else None
            # Check if next char is a vowel sign or halant
            if next_char and next_char in VOWELS_SIGNS:
                result.append(base_l)
            else:
                # Add inherent 'a' unless at end of word or before space
                if next_char and next_char != ' ':
                    result.append(base_l + 'a')
                else:
                    result.append(base_l)
        elif char in MATRAS_MAP:
            result.append(MATRAS_MAP[char])
        else:
            result.append(char)
    res_str = "".join(result).strip()
    return re.sub(r'\s+', ' ', res_str)

def compute_phonetic_fuzzy_similarity(name1: str, dev1: str, name2: str, dev2: str) -> float:
    n1_clean = name1.strip().lower() if name1 else ""
    n2_clean = name2.strip().lower() if name2 else ""

    dev1_latin = devanagari_to_latin(dev1).lower() if dev1 else ""
    dev2_latin = devanagari_to_latin(dev2).lower() if dev2 else ""

    candidates1 = [n for n in [n1_clean, dev1_latin] if n]
    candidates2 = [n for n in [n2_clean, dev2_latin] if n]

    best_score = 0.0

    for cand1 in candidates1:
        for cand2 in candidates2:
            w_ratio = fuzz.WRatio(cand1, cand2) / 100.0
            token_sort = fuzz.token_sort_ratio(cand1, cand2) / 100.0
            score = max(w_ratio, token_sort)

            try:
                m1 = jellyfish.metaphone(cand1)
                m2 = jellyfish.metaphone(cand2)
                if m1 and m2 and m1 == m2:
                    score = min(1.0, score + 0.15)
            except Exception:
                pass

            if score > best_score:
                best_score = score

    return float(best_score)
