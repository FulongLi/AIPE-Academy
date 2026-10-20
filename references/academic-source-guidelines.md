# Academic source guidelines

How AIPE Academy uses external academic material, and the rules every lesson,
reference record and website page must follow. These guidelines implement the
copyright, licensing and attribution requirements of v0.2 and apply to MIT
OpenCourseWare (MIT OCW) and to any other university course, textbook, review
paper or standard that is added later.

## 1. The relationship in one sentence

**External sources provide an academic reference baseline for scope and depth.
AIPE Academy independently develops the educational experience.**

A reference tells us *what* a rigorous programme covers and *how deep* it goes.
It never becomes the text of an AIPE lesson.

## 2. Licences are not interchangeable

| Material | Licence | Consequence |
| --- | --- | --- |
| AIPE Academy content (lessons, labs, exercises, figures, metadata) | CC BY 4.0 (`LICENSE.md`) | Anyone may reuse and adapt with attribution, including commercially. |
| MIT OpenCourseWare course content | Generally CC BY-NC-SA 4.0, with source-specific exceptions and third-party rights ([MIT OCW terms](https://ocw.mit.edu/pages/privacy-and-terms-of-use/)) | Non-commercial, share-alike; incompatible with CC BY 4.0 redistribution. |
| Textbooks, publisher pages, standards | All rights reserved unless stated | Link to the official record only. |

Because CC BY-NC-SA material cannot be relicensed as CC BY, **no MIT lecture
notes, figures, problem sets, exams, videos, textbooks or substantial text may
be copied, closely paraphrased or redistributed in this repository**. Where a
resource would require incompatible licensing, keep an external link.

Do not change AIPE Academy's licence without explicit maintainer approval.

## 3. What we record about a source

For every course in `references/mit-ocw-catalogue.json` the following facts are
read from the official page and its `data.json` by
`scripts/verify_academic_sources.py` and stored under `verified`:

- official title, course number(s), term and year, level, instructors as listed;
- the public learning-resource types MIT states (lecture notes, videos, problem
  sets ...), and the URLs of the public sub-pages (syllabus, lecture notes
  listing, video gallery, problem sets ...);
- the HTTP outcome, the canonical URL after redirects and the verification date.

Facts that MIT does not publish are never invented: no lecture numbers, chapter
titles, instructor details or resources beyond what the pages list. Topic
coverage is recorded as short topic or lecture titles (at most twelve words, as
listed) with the URL of the page they appear on, in `references/mit-ocw-coverage.json`.

The curated fields (priority, topic tags, mapped modules, coverage notes, gaps)
are AIPE Academy's own judgement and are labelled as such.

## 4. Verification status vocabulary

| Status | Meaning |
| --- | --- |
| `verified` | Page and `data.json` reached; number, title and term match the record. |
| `verified-with-differences` | Page reached; MIT states a different title, number or term (listed under `expectation_mismatches`). |
| `page-only` | Page reached but `data.json` could not be read. |
| `unavailable` | The recorded URL did not resolve when last checked. |
| `pending-review` | Not yet checked. |

Network verification is deliberate and separate from the offline test suite:
`python scripts/verify_academic_sources.py --update` refreshes the verified
fields and writes `references/mit-ocw-verification.json`; CI runs it only on
`workflow_dispatch`. An unavailable course is reported, never silently treated
as valid. Where a course has been renamed, replaced or moved, record the
verified canonical URL and keep the former URL in the notes.

## 5. How lessons cite references

Every standard-format lesson has an **Academic References** section:

```markdown
## Academic References

### MIT OpenCourseWare

Primary academic reference:

- MIT 6.622 — Power Electronics (Spring 2023)
- https://ocw.mit.edu/courses/6-622-power-electronics-spring-2023/

Relevant subjects:
- DC/DC converters
- Converter modelling

This lesson has been independently developed by AIPE Academy with reference to
the academic scope of the above course. MIT OpenCourseWare is an external
educational resource released under its own licence (generally CC BY-NC-SA 4.0).
AIPE Academy is not affiliated with or endorsed by MIT.
```

Rules:

1. Cite by stable reference id in the lesson's catalogue record
   (`academic_references: ["mit-6-622-2023"]`). The build fails if the lesson
   text does not link the course's official URL, so prose and metadata cannot
   drift apart.
2. Use the verified title and term from the catalogue, never from memory.
3. Link sub-pages (syllabus, lecture notes listing) only when they are listed
   in the verified record.
4. Keep the non-affiliation statement verbatim.
5. Do not turn a lesson into a list of external links: the lesson is the
   learning experience; references show where it sits academically.

The website renders the same ids through the generated projection
(`generated/academic-references.json`) and labels the panel as external.

## 6. Attribution of third-party material

- Preserve the ownership and licence notices of any third-party resource that
  is linked (publisher records, standards bodies, software projects).
- Material migrated from the AIPE website keeps its author, revision and
  licence in `references/website-migration.json`.
- Never imply MIT endorsement, academic certification or institutional
  affiliation in lesson text, website copy, plugin descriptions or marketing.

## 7. Adding a new external source

1. Add a record to `references/mit-ocw-catalogue.json` (or a sibling catalogue
   for another institution) with curated fields and `resource_status:
   pending-review`.
2. Run `python scripts/verify_academic_sources.py --update --only <id>`.
3. Map the source onto taxonomy modules with evidence URLs and coverage labels
   (`core`, `partial`, `introductory`, `background`).
4. Run `python scripts/build_catalogue.py` and the tests.
5. Record gaps honestly: an academic topic being covered by a source does not
   mean an AIPE lesson exists.

## 8. Checklist for reviewers

- [ ] Facts come from the official page; inferences are labelled.
- [ ] No copied or closely paraphrased external text, figures or problems.
- [ ] Official URLs link to the exact course edition and, where possible, the
      relevant syllabus or resource page.
- [ ] Non-affiliation statement present wherever a reference is shown.
- [ ] Verification date recorded; unavailable resources reported.
- [ ] AIPE licence unchanged.
