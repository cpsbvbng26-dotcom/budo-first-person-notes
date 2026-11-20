#!/usr/bin/env python3
"""The checks of budo-first-person-notes.

  python3 verification/check.py            offline: the records against the quotations kept in verification/sources.json
  python3 verification/check.py --online   fetch the source pages again from main of cpsbvbng26-dotcom and look for every quotation
  python3 verification/check.py --break    every check fails when the thing it watches is broken (offline)

The record of experience holds only what the operator has stated in public records. Each entry names the quotations it
rests on, and every number, date and grade in an entry must be found in those quotations. Verification is a separate file
and a separate section; it says what would count as checking and claims nothing.
"""
import json
import os
import re
import sys
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rules  # noqa: E402
from rules import add, jload, sub  # noqa: E402

PROSE = ["README.md", "README.en.md"]
EXP = "records/experience.json"
VER = "records/verification.json"
SRC = "verification/sources.json"
KINDS = {"statement": ("本人が述べたこと", "Statement"), "self-reported": ("本人の申告", "Self-reported"),
         "own account": ("本人の受け止め", "Own account")}
ENTRY_FIELDS = {"id", "kind", "ja", "en", "sources"}
ITEM_FIELDS = {"id", "about", "ja", "en", "status"}
STATUS = {"not done": ("していない", "Not done")}
ACCOUNT = ("これは私自身の受け止めとして書くもので、確かめた事実ではありません。", "This is my own account, not a verified fact.")
UA = {"User-Agent": "budo-first-person-notes-check/1.0 (+https://github.com/cpsbvbng26-dotcom/budo-first-person-notes)"}

# Names that this record does not write: the founders of the lineages of aikido, in kanji and in Latin letters
# (cpsbvbng26-dotcom's check_ecosystem.js 13j keeps the same four). The teacher's name is not known to this repository
# and is not written in any form; the checks below also stop a name-like word placed before 師範 and the word for "teacher"
# used as a title after a name.
NAMES = [rules.dec(x) for x in ("6Jek5bmz", "5qSN6Iqd", "dG9oZWk=", "dWVzaGliYQ==")]


def entries(F):
    return (jload(F, EXP) or {}).get("entries", [])


def items(F):
    return (jload(F, VER) or {}).get("items", [])


def quotes(F):
    return (jload(F, SRC) or {}).get("quotes", {})


def section(text, head):
    i = text.find("\n" + head + "\n")
    if i < 0:
        return ""
    j = text.find("\n## ", i + len(head) + 2)
    return text[i:j if j >= 0 else len(text)]


def table_rows(text, head):
    i = text.find("\n" + head + "\n")
    if i < 0:
        return None
    rows = []
    for line in text[i + 1:].split("\n")[2:]:
        if not line.startswith("|"):
            break
        rows.append([c.strip() for c in line.strip().strip("|").split(" | ")])
    return rows


def jdate(s):
    """2020 年 1 月 1 日 -> 2020-01-01."""
    return re.sub(r"(\d{4}) 年 (\d{1,2}) 月 (\d{1,2}) 日", lambda m: "%s-%02d-%02d" % (m.group(1), int(m.group(2)), int(m.group(3))), s)


# ------------------------------------------------------------------ the records

def schema(F):
    bad = []
    E, I, Q = entries(F), items(F), quotes(F)
    if not E or not I:
        return ["the records cannot be read"]
    ids = [e.get("id") for e in E]
    if ids != ["E%d" % n for n in range(1, len(E) + 1)]:
        bad.append("entries are not numbered E1, E2, ... in order")
    for e in E:
        if set(e) != ENTRY_FIELDS:
            bad.append("%s: the fields of an entry of experience (%s)" % (e.get("id"), ", ".join(sorted(set(e) ^ ENTRY_FIELDS))))
        if e.get("kind") not in KINDS:
            bad.append("%s: a kind outside the vocabulary" % e.get("id"))
        if not e.get("sources") or any(s not in Q for s in e.get("sources", [])):
            bad.append("%s: a source that is not a kept quotation" % e.get("id"))
        if e.get("kind") == "own account" and (ACCOUNT[0] not in e.get("ja", "") or ACCOUNT[1] not in e.get("en", "")):
            bad.append("%s: an own account without the words that it is not a verified fact" % e.get("id"))
    vids = [i.get("id") for i in I]
    if vids != ["V%d" % n for n in range(1, len(I) + 1)]:
        bad.append("items are not numbered V1, V2, ... in order")
    covered = set()
    for i in I:
        if set(i) != ITEM_FIELDS:
            bad.append("%s: the fields of an item of verification (%s)" % (i.get("id"), ", ".join(sorted(set(i) ^ ITEM_FIELDS))))
        if not i.get("about") or any(a not in ids for a in i.get("about", [])):
            bad.append("%s: about an entry that does not exist" % i.get("id"))
        covered |= set(i.get("about", []))
    if covered != set(ids):
        bad.append("an entry of experience with no item of verification: " + ", ".join(sorted(set(ids) - covered)))
    for k, q in Q.items():
        if set(q) != {"file", "text"} or not q.get("text"):
            bad.append("the quotation " + k)
    return bad


# Words of kanji that an entry may use although its sources do not: the form of a sentence, not a fact.
OWN_WORDS = {"年経験", "稽古"}


def against_sources(F):
    """Every number, date and grade in an entry is in the quotations the entry names."""
    bad = []
    Q = quotes(F)
    for e in entries(F):
        src = jdate(" ".join(Q.get(s, {}).get("text", "") for s in e.get("sources", [])))
        for m in re.finditer(r"\d{4}-\d{2}-\d{2}|\d+(?= 年)", e.get("ja", "")):
            if m.group(0) not in src:
                bad.append("%s: %s is not in its sources" % (e.get("id"), m.group(0)))
        for w in ("五級", "初級", "心身統一合氣道会", "栃木", "氣の原理・統一体・体技・合氣剣・合氣杖・合氣短刀", "高い評価", "最後"):
            if w in e.get("ja", "") and w not in src:
                bad.append("%s: 「%s」 is not in its sources" % (e.get("id"), w))
        for w in re.findall(r"[一-龥々]{2,}", e.get("ja", "")):
            if w not in src and w not in OWN_WORDS:
                bad.append("%s: the word「%s」 is in no source it names" % (e.get("id"), w))
        nums_ja = re.findall(r"\d+(?:-\d+)*", e.get("ja", ""))
        nums_en = re.findall(r"\d+(?:-\d+)*", e.get("en", ""))
        if sorted(nums_ja) != sorted(nums_en):
            bad.append("%s: the numbers of the two languages differ" % e.get("id"))
    return bad


def years_total(F):
    m = re.search(r"本場である栃木で通算 (\d+) 年", quotes(F).get("solitary-years", {}).get("text", ""))
    return int(m.group(1)) if m else None


def years_teacher(F):
    m = re.search(r"師範に (\d+) 年間師事", quotes(F).get("coi-teacher", {}).get("text", ""))
    return int(m.group(1)) if m else None


def years_and_grades(F):
    """The years agree across the record of conflicts of interest and the page on the solitary school; the years under
    the teacher do not exceed them; the grades and their date are those of the CV, which calls them self-reported."""
    bad = []
    Q = quotes(F)
    m = re.search(r"心身統一合氣道を (\d+) 年間経験しました", Q.get("coi-years", {}).get("text", ""))
    total, teacher = years_total(F), years_teacher(F)
    if not m or total is None or int(m.group(1)) != total:
        bad.append("the years in the record of conflicts of interest and on the page on the solitary school differ")
    if teacher is None or total is None or not 0 < teacher <= total:
        bad.append("the years under the teacher exceed the years of training")
    days = set()
    for k, grade in (("cv-gokyu", "心身統一合氣道 五級"), ("cv-shokyu", "心身統一道 初級")):
        t = jdate(Q.get(k, {}).get("text", ""))
        d = re.search(r"\d{4}-\d{2}-\d{2}", t)
        if grade not in t or not d:
            bad.append("the CV quotation " + k)
            continue
        days.add(d.group(0))
    if "本人の申告です。" not in Q.get("cv-self-reported", {}).get("text", ""):
        bad.append("the CV does not call the grades self-reported")
    E = {e["id"]: e for e in entries(F)}
    for i, grade in (("E4", "五級"), ("E5", "初級")):
        e = E.get(i, {})
        if grade not in e.get("ja", "") or e.get("kind") != "self-reported" or not days or ("免状の日付は %s です。" % min(days)) not in e.get("ja", ""):
            bad.append(i + ": the grade, its date or its kind differs from the CV")
    if len(days) != 1:
        bad.append("the two grades of the CV no longer share one date")
    return bad


def readme_tables(F):
    """Both READMEs carry the entries and the items word for word, with the kinds and the statuses of the vocabularies."""
    bad = []
    E, I = entries(F), items(F)
    for f, n, eh, vh in (("README.md", 0, "| 番号 | 記録 | 種類 | 出どころ |", "| 番号 | 対象 | 確かめたことになるもの | 状態 |"),
                         ("README.en.md", 1, "| No. | Record | Kind | Source |", "| No. | About | What would count as checking | Status |")):
        t = F.get(f, "")
        rows = table_rows(t, eh)
        want = [[e["id"], e["ja" if n == 0 else "en"], KINDS.get(e["kind"], ("?", "?"))[n]] for e in E]
        if rows is None or [r[:3] for r in rows] != want:
            bad.append(f + ": the table of experience is not records/experience.json")
        rows = table_rows(t, vh)
        sep = "、" if n == 0 else ", "
        want = [[i["id"], sep.join(i["about"]), i["ja" if n == 0 else "en"], STATUS.get(i["status"], ("?", "?"))[n]] for i in I]
        if rows is None or rows != want:
            bad.append(f + ": the table of verification is not records/verification.json")
    return bad


CLAIM = re.compile(r"確かめました|確認しました|検証しました|確かめてあります|確認済み|検証済み|裏付けられ|\bverified\b|\bconfirmed\b|\bhas been checked\b|\bwas checked\b", re.I)
HEADS = {"README.md": ("## 開示", "## 体験の記録", "## 検証", "## 扱わないこと"),
         "README.en.md": ("## Disclosure", "## Record of experience", "## Verification", "## Not handled here")}


def separation(F):
    """Experience and verification are apart: the sections come in order, the record of experience claims no checking,
    and every item of verification is not done."""
    bad = []
    for f, heads in HEADS.items():
        t = F.get(f, "")
        at = [t.find("\n" + h + "\n") for h in heads]
        if any(a < 0 for a in at) or at != sorted(at):
            bad.append(f + ": the sections of disclosure, experience, verification and what is not handled, in that order")
            continue
        exp = section(t, heads[1]).replace(ACCOUNT[0], "").replace(ACCOUNT[1], "").replace("not a verified fact", "")
        if CLAIM.search(exp):
            bad.append(f + ": the record of experience claims a check「" + CLAIM.search(exp).group(0) + "」")
        ver = section(t, heads[2])
        if CLAIM.search(ver.replace("No part of this record claims that anything was checked.", "").replace("None of the entries has been checked.", "")):
            bad.append(f + ": the section of verification claims a check")
    if "どの項目も、まだ確かめていません。" not in F.get("README.md", "") or "None of the entries has been checked." not in F.get("README.en.md", ""):
        bad.append("the READMEs do not say that nothing has been checked")
    for i in items(F):
        if i.get("status") != "not done":
            bad.append(i.get("id", "?") + ": an item of verification that is not 'not done'")
    for e in entries(F):
        if CLAIM.search(e.get("ja", "") + e.get("en", "").replace("not a verified fact", "")):
            bad.append(e.get("id", "?") + ": an entry of experience claims a check")
    return bad


DISCLOSE = {
    "README.md": ["(https://github.com/cpsbvbng26-dotcom/cpsbvbng26-dotcom/blob/main/docs/conflicts-of-interest.md)",
                  "稽古の所属団体は、心身統一合氣道会です。", "この記録は、団体の承認を受けたものではありません。",
                  "師範の名は書きません。", "師範を特定できる言い方もしません。",
                  "この記録は、新しい研究の主題を始めるものではありません。", "独学の系列に、この主題を足しません。",
                  "JOSS、ダイヤモンド・オープンアクセスの場、学会発表、共同研究などの経路です。"],
    "README.en.md": ["(https://github.com/cpsbvbng26-dotcom/cpsbvbng26-dotcom/blob/main/docs/conflicts-of-interest.en.md)",
                     "This record has not been approved by the organisation.", "The teacher's name is not written.",
                     "Nor is anything that would identify the teacher.", "This record does not start a new research topic.",
                     "The subject is not added to the self-taught series.",
                     "These are routes such as JOSS, diamond open access venues, conference presentations and joint research."],
}


def disclosure(F):
    """The disclosure points to the record of conflicts of interest and restates its conditions word for word."""
    bad = []
    Q = quotes(F)
    for f, must in DISCLOSE.items():
        t = section(F.get(f, ""), HEADS[f][0]) + F.get(f, "")[:F.get(f, "").find("\n## ")]
        for s in must:
            if s not in t:
                bad.append(f + ": the disclosure lacks「" + s[:30] + "」")
    for f, k in (("README.md", "coi-conditions"), ("README.en.md", "coi-en-conditions")):
        want = "\n".join("- " + line for line in Q.get(k, {}).get("text", "?").split("\n"))
        if want not in section(F.get(f, ""), HEADS[f][0]):
            bad.append(f + ": the conditions of the record of conflicts of interest are not restated word for word")
    for k in ("coi-no-name", "coi-not-approved", "coi-series"):
        for line in Q.get(k, {}).get("text", "?").split("\n"):
            if line not in F.get("README.md", ""):
                bad.append("README.md: the disclosure lacks the record's own sentence「" + line[:20] + "」")
    return bad


NOT_HANDLED = {"README.md": ["氣の効果について、何も主張しません。肯定も否定もしません。", "Sophaxis のことは、この記録では扱いません。",
                             "氣の原理を、独学の系列の研究の主題にしません。"],
               "README.en.md": ["No claim is made about the effects of ki, either for or against.", "Sophaxis is not handled in this record.",
                                "The principle of ki is not made a research topic of the self-taught series."]}
EFFECT = re.compile(r"効果が(?:ある|あり|あった|出)|効能|効き目|治(?:る|った|療)|癒(?:す|し|え)|健康に(?:よい|良い)|"
                    r"\b(?:heals?|healing|cures?|therapeutic|effective|efficacy|improves? (?:health|the body))\b", re.I)


def not_handled(F):
    """What is not handled is said in both READMEs, and nothing anywhere claims an effect of ki. Sophaxis is named only
    in the sentence that says it is not handled."""
    bad = []
    for f, must in NOT_HANDLED.items():
        sec = section(F.get(f, ""), HEADS[f][3])
        for s in must:
            if s not in sec:
                bad.append(f + ": what is not handled lacks「" + s[:24] + "」")
    for f, t in F.items():
        if f not in PROSE + [EXP, VER, SRC, ".zenodo.json"]:
            continue
        m = EFFECT.search(t)
        if m:
            bad.append(f + ": a claim about an effect「" + m.group(0) + "」")
        rest = t.replace(NOT_HANDLED["README.md"][1], "").replace(NOT_HANDLED["README.en.md"][1], "")
        if f in PROSE and "Sophaxis" in rest:
            bad.append(f + ": Sophaxis is named outside the sentence that says it is not handled")
    return bad


def person_names(F):
    """No name of a person of the school: the founders' names (kept in base64), no word for 'teacher' as a title after a
    name, and no name-like word glued to 師範."""
    bad = []
    for f, t in F.items():
        if f in ("verification/check.py", "verification/rules.py"):
            continue
        n = rules.norm(t)
        for w in NAMES:
            if w.casefold() in n:
                bad.append(f + ": a person's name")
        if re.search(r"[一-龥ァ-ヴー]師範|先生|\bsensei\b", t, re.I):
            bad.append(f + ": a name or title glued to the teacher")
    return bad


COUNTERS = {"years_total": years_total, "years_teacher": years_teacher}

CHECKS = [
    ("The records: fields, kinds, numbering, sources that are kept quotations, own accounts that say so, an item of verification for every entry", schema),
    ("Every number, date and grade in an entry is in the quotations it names, in both languages", against_sources),
    ("The years agree with the page on the solitary school, the years under the teacher do not exceed them, and the grades and their date are the CV's", years_and_grades),
    ("Both READMEs carry the entries and the items of verification word for word", readme_tables),
    ("Experience and verification are apart: sections in order, no claim of a check in the record of experience, every item not done", separation),
    ("The disclosure links the record of conflicts of interest and restates its conditions, the name rule and rule 15", disclosure),
    ("What is not handled is said in both READMEs; nothing claims an effect of ki; Sophaxis only where it is set aside", not_handled),
    ("No name of a person of the school", person_names),
    ("Copies of the canonical files and the licences are byte-identical (sha256)", rules.copies),
    ("No name of the operator's own university in any spelling, other place of creative work, self-title, item of rule 10 or single relative", rules.words_not_written),
    ("No subject that these repositories do not write about", rules.topics_not_written),
    ("No list of work for the operator", rules.no_tasks),
    ("No e-mail address in any file", rules.no_email),
    ("Workflows: actions pinned to commits, permissions, timeouts; Dependabot", rules.workflows),
    ("labels.yml makes the labels of the canonical workflows", lambda F: rules.labels(F)),
    ("CLAUDE.md carries rules 16, 17 and 18 (10 times)", rules.claude_md),
    ("The writing rules: です/ます, no second person, no bold, one dash per paragraph, short sentences", lambda F: rules.prose(F, PROSE)),
    ("Every number in prose is in the ledger of numbers, and every count matches the sources", lambda F: rules.numbers(F, PROSE, COUNTERS, PROSE)),
    ("README.md and README.en.md link each other, disclose the language model and name the licences", rules.readme_pair),
    (".zenodo.json: one creator with the ORCID iD, the licence of LICENSE, the disclosure, the licence sentence, related identifiers found in the repository", rules.zenodo),
]


def online(F):
    S = jload(F, SRC)
    bad, files = [], {}
    for k, q in S["quotes"].items():
        f = q["file"]
        if f not in files:
            url = "https://raw.githubusercontent.com/%s/main/%s" % (S["repository"], f)
            try:
                with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as r:
                    files[f] = r.read().decode("utf-8")
            except Exception as e:
                files[f] = None
                bad.append("%s could not be fetched: %s" % (f, e))
        if files[f] is not None and q["text"] not in files[f]:
            bad.append("%s: the quotation %s is no longer in %s on main" % (S["repository"], k, f))
    for b in bad:
        print("  FAIL  " + b)
    print("\nonline: %d files, %d quotations, %d problems." % (len(files), len(S["quotes"]), len(bad)))
    return 1 if bad else 0


C = [c[0] for c in CHECKS]
BREAKS = [
    (C[0], "an entry with a field of verification", sub(EXP, '"id": "E2",', '"id": "E2",\n      "status": "checked",')),
    (C[0], "an entry citing a quotation that is not kept", sub(EXP, '"sources": ["coi-org"]', '"sources": ["coi-dojo"]')),
    (C[0], "a kind outside the vocabulary", sub(EXP, '"kind": "statement",\n      "ja": "稽古の所属団体', '"kind": "memory",\n      "ja": "稽古の所属団体')),
    (C[0], "an own account without its disclaimer", sub(EXP, "これは私自身の受け止めとして書くもので、確かめた事実ではありません。", "")),
    (C[0], "an entry with no item of verification", sub(VER, '"about": ["E6"]', '"about": ["E5"]')),
    (C[1], "an entry says 8 years", sub(EXP, "通算 7 年経験しました", "通算 8 年経験しました")),
    (C[1], "an entry names a place its source does not", sub(EXP, "本場である栃木です。", "本場である東京です。")),
    (C[1], "the English entry gives another number", sub(EXP, "For 4 years I studied", "For 5 years I studied")),
    (C[2], "the page on the solitary school says 8 years", sub(SRC, "本場である栃木で通算 7 年。", "本場である栃木で通算 8 年。")),
    (C[2], "the years under the teacher exceed the years of training", sub(SRC, "師範に 4 年間師事", "師範に 9 年間師事")),
    (C[2], "the CV moves the date of the fifth kyu", sub(SRC, "<p>心身統一合氣道 五級<span>2020 年 1 月 1 日", "<p>心身統一合氣道 五級<span>2019 年 1 月 1 日")),
    (C[2], "an entry gives the grade another date", sub(EXP, "心身統一道の初級を受けました。免状の日付は 2020-01-01 です。", "心身統一道の初級を受けました。免状の日付は 2021-01-01 です。")),
    (C[3], "README.md changes an entry", sub("README.md", "| E2 | 稽古の所属団体は、心身統一合氣道会です。 |", "| E2 | 稽古の所属団体は、合氣道の会です。 |")),
    (C[3], "README.en.md marks an item done", sub("README.en.md", "under rule 10. | Not done |", "under rule 10. | Done |")),
    (C[4], "the record of experience claims a check", sub("README.md", "各項目の出どころは、`verification/sources.json` の引用です。", "各項目は、団体の記録で確かめました。")),
    (C[4], "an item of verification is marked done", sub(VER, '"status": "not done"', '"status": "done"')),
    (C[4], "the section of verification comes before experience", lambda G: G.__setitem__("README.md", G["README.md"].replace("## 体験の記録\n", "## 体験の記録の前\n", 1).replace("## 検証\n", "## 体験の記録\n", 1).replace("## 体験の記録の前\n", "## 検証\n", 1))),
    (C[4], "the English record of experience says it was confirmed", sub("README.en.md", "No experience of training is added here.", "Every entry was confirmed by the organisation.")),
    (C[5], "README.en.md drops the link to the record of conflicts of interest", sub("README.en.md", "docs/conflicts-of-interest.en.md) of cpsbvbng26-dotcom", "docs/governance.md) of cpsbvbng26-dotcom")),
    (C[5], "README.md drops a condition", sub("README.md", "- 体験と検証を分けた形にします。\n", "")),
    (C[5], "README.md drops rule 15", sub("README.md", "独学の系列に、この主題を足しません。", "この記録は当事者の記録です。")),
    (C[5], "README.md drops that the organisation did not approve it", sub("README.md", "この記録は、団体の承認を受けたものではありません。\n", "")),
    (C[6], "a claim about an effect of ki", add("README.md", "\n氣の原理には、体を整える効果があります。\n")),
    (C[6], "README.en.md drops that it makes no claim", sub("README.en.md", "- No claim is made about the effects of ki, either for or against.\n", "")),
    (C[6], "README.md names Sophaxis elsewhere", add("README.md", "\nこの記録は Sophaxis に載せます。\n")),
    (C[7], "a founder's name", add("README.md", "\n" + NAMES[0] + "\n")),
    (C[7], "a founder's name in Latin letters", add("README.en.md", "\n" + NAMES[3].capitalize() + "\n")),
    (C[7], "a name glued to the teacher", sub("README.md", "そのうち 4 年は、師範に師事しています。", "そのうち 4 年は、山" + "田師範に師事しています。")),
    (C[8], "one character of SECURITY.md", sub("SECURITY.md", "7 日以内", "8 日以内")),
    (C[8], "the note on the copies says the cross-repository check compares them all", sub("verification/copies.json", "そのほかの写しについては、横断の検査は、まだこのリポジトリを見ていません。", "横断の検査も、七つの写しを正本と突き合わせます。")),
    (C[9], "the university's name, romanised", add("README.md", "\n" + rules.dec("emVu") + " " + rules.dec("ZGFpZ2FrdQ==") + "\n")),
    (C[9], "a word for a single relative", add("README.md", "\n" + rules.RELATIVES[0] + "\n")),
    (C[9], "an item of rule 10", add("README.en.md", "\n" + rules.dec("c2VhbGFuZA==") + "\n")),
    (C[10], "a degree these repositories do not write about", add("README.en.md", "\n" + rules.dec("TUJB") + "\n")),
    (C[10], "a word for a political organisation", add("README.md", "\n" + rules.dec("5pS/5YWa") + "\n")),
    (C[11], "a list of work for the operator", add("README.md", "\n免状は" + "運営者が確かめる。\n")),
    (C[12], "an e-mail address", add("records/experience.json", "\nwriter" + "@" + "example.com\n")),
    (C[13], "an action named by its version", sub(".github/workflows/check.yml", "actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1", "actions/checkout@v7")),
    (C[13], "the check writes", sub(".github/workflows/check.yml", "contents: read", "contents: write")),
    (C[14], "labels.yml drops a label", sub(".github/workflows/labels.yml", 'gh label create "erratum"', 'gh label create "error"')),
    (C[15], "CLAUDE.md loses rule 17", sub("CLAUDE.md", "`list_issues` で一覧を取らない", "`list_issues` で一覧を取る")),
    (C[16], "a sentence not in です/ます", add("README.md", "\n記録は一人称で書く。\n")),
    (C[16], "you in English", add("README.en.md", "\nYour record is here.\n")),
    (C[17], "the prose says 8 years", sub("README.md", "運営者は、心身統一合氣道を通算 7 年経験しました。", "運営者は、心身統一合氣道を通算 8 年経験しました。")),
    (C[17], "the English prose says 5 years under the teacher", sub("README.en.md", "For 4 of those years", "For 5 of those years")),
    (C[17], "a number not in the ledger of numbers", add("README.md", "\n稽古は 300 回でした。\n")),
    (C[18], "README.md does not link the English page", sub("README.md", "[English](./README.en.md)", "English")),
    (C[19], ".zenodo.json loses the disclosure", sub(".zenodo.json", "Claude is not an author.", "Claude helped.")),
    (C[19], ".zenodo.json gives an affiliation", sub(".zenodo.json", '"orcid": "0009-0000-1406-0547"', '"orcid": "0009-0000-1406-0547", "affiliation": "x"')),
    (C[19], ".zenodo.json names the MIT licence", sub(".zenodo.json", '"license": "cc-by-4.0"', '"license": "mit"')),
    (C[19], ".zenodo.json names another repository in the title", sub(".zenodo.json", '"title": "budo-first-person-notes: ', '"title": "self-correction: ')),
]

if __name__ == "__main__":
    F = rules.load()
    if "--online" in sys.argv:
        sys.exit(online(F))
    sys.exit(rules.run(CHECKS, BREAKS, F, sys.argv))
