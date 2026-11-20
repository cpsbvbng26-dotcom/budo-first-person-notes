# budo-first-person-notes

[日本語](./README.md)

A first-person record by the operator, who trained in Shinshin Toitsu Aikido (心身統一合氣道).
The [record of conflicts of interest](https://github.com/cpsbvbng26-dotcom/cpsbvbng26-dotcom/blob/main/docs/conflicts-of-interest.en.md) of cpsbvbng26-dotcom allows the principle of ki to be handled only as a first-person record.
This repository is that first-person record.
Experience and verification are kept in separate sections and separate files.

The archive is on Zenodo. The DOI of the first version is [`10.5281/zenodo.24396795`](https://doi.org/10.5281/zenodo.24396795), and the DOI common to all versions is [`10.5281/zenodo.24396794`](https://doi.org/10.5281/zenodo.24396794).

## Disclosure

This record was set down on 2026-11-20.
The operator trained in Shinshin Toitsu Aikido for 7 years in all.
For 4 of those years, the operator studied under a teacher (師範).
The organisation the operator trained under is the Shinshin Toitsu Aikido Kai (心身統一合氣道会).
The name of the organisation is written to disclose the history of affiliation.
This record has not been approved by the organisation.
Its name is not used to support any claim.
The teacher's name is not written.
Nor is anything that would identify the teacher.
This is because rule 10 of cpsbvbng26-dotcom limits what is written about living persons.

The record of conflicts of interest sets these conditions:

- If it is handled at all, it is only as a first-person record.
- My position and the relationship between teacher and student are disclosed.
- Experience is kept apart from verification.
- It is not handled in any form that lacks one of these.

This record is built to meet all of them.
The position and the relationship between teacher and student are disclosed in this section.
Experience is in the section "Record of experience" and in `records/experience.json`.
Verification is in the section "Verification" and in `records/verification.json`.

A record written from this position is not neutral.
Writing in favour would support the operator's own background and the authority of the teacher and the school.
Writing against would be subject to deference to, or pressure from, the relationship between teacher and student.

### The self-taught series

This record does not start a new research topic.
The subject is not added to the self-taught series.
Under rule 15 of cpsbvbng26-dotcom, the self-taught work is what was done up to the first undergraduate year.
This is a first-person record, not self-taught work.
If the principle of ki is ever handled as research, it goes by the routes that rule 15 names.
These are routes such as JOSS, diamond open access venues, conference presentations and joint research.

## Record of experience

This section is written in the first person.
It holds only what the operator has already stated in public records.
No experience of training is added here.
The source of each entry is a quotation in `verification/sources.json`.

| No. | Record | Kind | Source |
| --- | --- | --- | --- |
| E1 | I trained in Shinshin Toitsu Aikido for 7 years in all. I trained in Tochigi, where the school has its home. | Statement | Record of conflicts of interest, page on the solitary school |
| E2 | The organisation I trained under is the Shinshin Toitsu Aikido Kai. | Statement | Record of conflicts of interest |
| E3 | For 4 years I studied under a teacher (師範). I learnt the principle of ki, the unified body (統一体), the empty-hand techniques (体技), and the sword, staff and knife of aikido (合氣剣・合氣杖・合氣短刀). | Statement | Record of conflicts of interest |
| E4 | I received fifth kyu (五級) of Shinshin Toitsu Aikido. The certificate is dated 2020-01-01. | Self-reported | CV |
| E5 | I received the first grade (初級) of Shinshin Toitsu Dō. The certificate is dated 2020-01-01. | Self-reported | CV |
| E6 | Fifth kyu was my last promotion in Shinshin Toitsu Aikido. | Statement | Record of conflicts of interest |
| E7 | In my time at fifth kyu, I take it that the teacher rated me highly. This is my own account, not a verified fact. | Own account | Record of conflicts of interest |

The sources are these pages of cpsbvbng26-dotcom:

- [Record of conflicts of interest](https://github.com/cpsbvbng26-dotcom/cpsbvbng26-dotcom/blob/main/docs/conflicts-of-interest.en.md)
- [The page on the solitary school](https://cpsbvbng26-dotcom.vercel.app/notes/solitary-school.html) (in Japanese)
- The section 「武道」 of [the CV](https://cpsbvbng26-dotcom.vercel.app/cv.html) (in Japanese)

## Verification

This section says only what would count as checking.
None of the entries has been checked.
No part of this record claims that anything was checked.

| No. | About | What would count as checking | Status |
| --- | --- | --- | --- |
| V1 | E1, E3 | Comparing the years of training, and the years under the teacher, with the membership records of the organisation or the dojo. | Not done |
| V2 | E2 | Comparing the history of affiliation with the records of the organisation. | Not done |
| V3 | E4, E5 | Someone other than the operator comparing the grades and the dates with the certificates themselves. The CV says the certificates are at hand. | Not done |
| V4 | E6 | Comparing which promotion was the last with the records of the organisation. | Not done |
| V5 | E7 | This record has no way to check this account. Neither the teacher's name nor the teacher's words are written, under rule 10. | Not done |

## Not handled here

- No claim is made about the effects of ki, either for or against.
- The teachings and techniques of the school are not explained from general knowledge.
- The teacher's name, and anything that would identify the teacher, are not written. Nor are the names of other students.
- Sophaxis is not handled in this record.
- The principle of ki is not made a research topic of the self-taught series.

## Form of the record

An entry of the record of experience has these fields.

| Field | Content |
| --- | --- |
| `id` | The number, starting with E |
| `kind` | The kind; one of the table below |
| `ja`・`en` | The first-person sentence: what the operator stated in public records |
| `sources` | The names of quotations in `verification/sources.json` |

| `kind` | Meaning |
| --- | --- |
| `statement` | Something the operator stated |
| `self-reported` | Self-reported: a grade and the date of its certificate |
| `own account` | The operator's own account; the same entry says it is not a verified fact |

An item of verification has the fields `id`, `about`, `ja`, `en` and `status`.
Every `status` is `not done` now.
Entries of experience carry no field of verification, and items of verification carry no sentence of experience.

## Checks

```
python3 verification/check.py            # fields, quotations, years and grades, the separation, the disclosure, names, copies, writing, numbers
python3 verification/check.py --online   # fetch the source pages again from main of cpsbvbng26-dotcom and look for the quotations
python3 verification/check.py --break    # break each check once and see it fail
```

CI runs the offline check and the breaking check on every push and pull request.
The online check runs as a separate job at the same times and once a week.

## Operator

The operator is Takuya Nemoto (根本卓哉).
ORCID iD: [0009-0000-1406-0547](https://orcid.org/0009-0000-1406-0547).
Errors are received through the [error report](https://github.com/cpsbvbng26-dotcom/budo-first-person-notes/issues/new?template=error-report.yml) form.
Security issues are received by the route in [SECURITY.md](./SECURITY.md).

## Use of language models

The use of language models is set out in the same table as in the other repositories.

| Tool | Used for | Checked by |
| --- | --- | --- |
| Claude Code (Anthropic) | The form of the record, README text, the checks in `verification/`, and the copies from the record of conflicts of interest and the other pages | The checks of `verification/check.py`; there is no record of the operator reading and checking it |

The sentences of the record of experience were put into the first person by Claude Code from what the operator stated in public records.
Claude is not an author.

## Licence

The text and the records are [CC BY 4.0](./LICENSE); the code is [MIT](./LICENSE-CODE).
