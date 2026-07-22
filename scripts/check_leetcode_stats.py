from __future__ import annotations

import re
import sys
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LEETCODE_ROOT = ROOT / "docs" / "csharp" / "leetcode"
MAIN_INDEX = LEETCODE_ROOT / "index.md"
CPP_INDEX = ROOT / "docs" / "cpp" / "leetcode" / "index.md"

DIFFICULTIES = ("Easy", "Medium", "Hard")
TABLE_ROW_RE = re.compile(
    r"^\|\s*\[[^\]]+\]\((?P<link>[^)]+)\)\s*\|\s*"
    r"(?P<difficulty>Easy|Medium|Hard)\s*\|\s*(?P<notes>.*?)\s*\|"
)
MAIN_DIFFICULTY_RE = re.compile(r"^\|\s*(Easy|Medium|Hard)\s*\|\s*(\d+)\s*\|", re.MULTILINE)
MAIN_TOTAL_RE = re.compile(
    r"\u5f53\u524d\u5171\u8bb0\u5f55\s+(\d+)\s+\u9053\u9898\uff0c"
    r"\u5176\u4e2d\s+(\d+)\s+\u9053"
)
CPP_BILINGUAL_COUNT_RE = re.compile(r"\u5f53\u524d\u53cc\u8bed\u5bf9\u7167\u6570\u91cf\uff1a\s*(\d+)")
BILINGUAL_MARK_RE = re.compile(r"C#\s*/\s*C\+\+\s*\u5bf9\u7167")
CPP_LINK_RE = re.compile(r"\]\(\.\./\.\./csharp/leetcode/[^)]+\)")
CPP_BILINGUAL_LIST_MARK = "\u5df2\u5f62\u6210\u53cc\u8bed\u5bf9\u7167"


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def parse_topic_indexes() -> tuple[Counter[str], int, list[str]]:
    counts: Counter[str] = Counter()
    bilingual_count = 0
    seen_links: set[Path] = set()
    errors: list[str] = []

    for index_path in sorted(LEETCODE_ROOT.glob("*/index.md")):
        for line_no, line in enumerate(read_text(index_path).splitlines(), start=1):
            match = TABLE_ROW_RE.match(line)
            if not match:
                continue

            difficulty = match.group("difficulty")
            link = match.group("link").strip()
            notes = match.group("notes")
            target = (index_path.parent / link).resolve()

            if target in seen_links:
                errors.append(f"duplicate topic-index entry: {target.relative_to(ROOT)}")
            seen_links.add(target)

            if not target.exists():
                errors.append(
                    f"missing problem page linked from {index_path.relative_to(ROOT)}:{line_no}: {link}"
                )

            counts[difficulty] += 1
            if BILINGUAL_MARK_RE.search(notes):
                bilingual_count += 1

    return counts, bilingual_count, errors


def parse_main_index() -> tuple[dict[str, int], int, int, list[str]]:
    text = read_text(MAIN_INDEX)
    errors: list[str] = []
    reported_counts = {difficulty: int(count) for difficulty, count in MAIN_DIFFICULTY_RE.findall(text)}

    missing_difficulties = [difficulty for difficulty in DIFFICULTIES if difficulty not in reported_counts]
    if missing_difficulties:
        errors.append(f"missing difficulty rows in {MAIN_INDEX.relative_to(ROOT)}: {missing_difficulties}")

    total_match = MAIN_TOTAL_RE.search(text)
    if not total_match:
        errors.append(f"missing total/bilingual summary in {MAIN_INDEX.relative_to(ROOT)}")
        return reported_counts, -1, -1, errors

    reported_total = int(total_match.group(1))
    reported_bilingual = int(total_match.group(2))
    return reported_counts, reported_total, reported_bilingual, errors


def parse_cpp_index() -> tuple[int, int, list[str]]:
    text = read_text(CPP_INDEX)
    errors: list[str] = []

    count_match = CPP_BILINGUAL_COUNT_RE.search(text)
    if not count_match:
        errors.append(f"missing bilingual count in {CPP_INDEX.relative_to(ROOT)}")
        reported_count = -1
    else:
        reported_count = int(count_match.group(1))

    bilingual_lines = [line for line in text.splitlines() if CPP_BILINGUAL_LIST_MARK in line]
    if not bilingual_lines:
        errors.append(f"missing bilingual link list in {CPP_INDEX.relative_to(ROOT)}")
        listed_links = -1
    else:
        listed_links = sum(len(CPP_LINK_RE.findall(line)) for line in bilingual_lines)

    return reported_count, listed_links, errors


def main() -> int:
    actual_counts, actual_bilingual, errors = parse_topic_indexes()
    reported_counts, reported_total, reported_bilingual, main_errors = parse_main_index()
    cpp_bilingual, cpp_links, cpp_errors = parse_cpp_index()
    errors.extend(main_errors)
    errors.extend(cpp_errors)

    actual_total = sum(actual_counts.values())

    for difficulty in DIFFICULTIES:
        if reported_counts.get(difficulty) != actual_counts[difficulty]:
            errors.append(
                f"{difficulty} count mismatch: index says {reported_counts.get(difficulty)}, "
                f"topic indexes contain {actual_counts[difficulty]}"
            )

    if reported_total != actual_total:
        errors.append(f"total mismatch: index says {reported_total}, topic indexes contain {actual_total}")

    if reported_bilingual != actual_bilingual:
        errors.append(
            f"main bilingual mismatch: index says {reported_bilingual}, "
            f"topic indexes mark {actual_bilingual}"
        )

    if cpp_bilingual != actual_bilingual:
        errors.append(
            f"C++ bilingual mismatch: C++ index says {cpp_bilingual}, "
            f"topic indexes mark {actual_bilingual}"
        )

    if cpp_links != actual_bilingual:
        errors.append(
            f"C++ bilingual link list mismatch: C++ index lists {cpp_links}, "
            f"topic indexes mark {actual_bilingual}"
        )

    if errors:
        print("LeetCode stats check failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    count_text = ", ".join(f"{difficulty}={actual_counts[difficulty]}" for difficulty in DIFFICULTIES)
    print(f"LeetCode stats OK: total={actual_total}, bilingual={actual_bilingual}, {count_text}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
