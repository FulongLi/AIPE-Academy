# MIT OpenCourseWare academic baseline

Generated from `references/mit-ocw-catalogue.json` and `references/mit-ocw-coverage.json` by
`scripts/build_reference_docs.py`; edit the JSON, not this file.

Machine-readable academic reference baseline. MIT OpenCourseWare courses whose public syllabi and teaching resources set the scope and depth AIPE Academy's four knowledge domains aim for. Facts under `verified` were read from the official course page and its data.json by scripts/verify_academic_sources.py; every other field is AIPE Academy's own curation and mapping.

**Relationship.** MIT OpenCourseWare provides an academic reference baseline. AIPE Academy independently develops its own explanations, derivations, exercises, code and simulations. AIPE Academy is not affiliated with or endorsed by MIT.

**Licence.** MIT OpenCourseWare publishes most course content under CC BY-NC-SA 4.0 with source-specific exceptions and third-party rights; see https://ocw.mit.edu/pages/privacy-and-terms-of-use/. AIPE Academy links to official URLs and records metadata only. No MIT lecture notes, figures, assignments, videos or textbooks are copied into this repository, and AIPE Academy's CC BY 4.0 licence does not extend to any MIT material.

## Verification summary

- Candidate courses reviewed: 22 (the 22 initial candidates of v0.2).
- Verification date(s): 2026-10-20; method: Each course page, syllabus, calendar and resource listing page was read as HTML by a mapping agent; a fact-checker re-fetched the cited pages and a curriculum reviewer checked the module mapping; corrections were applied before writing. Only short listing titles and page URLs are stored..
- Status counts: `verified` 22.
- Facts under *Verified* were read from the official MIT OCW page and its `data.json`; *Topic coverage* titles were read from the public syllabus, calendar and resource listing pages (URLs in the coverage file); *AIPE mapping* is AIPE Academy's own judgement.
- Re-run: `python scripts/verify_academic_sources.py --update` (network), then `python scripts/build_reference_docs.py`.

| Status | Meaning |
| --- | --- |
| `verified` | Official page and data.json reached; course number, title and term match this record. |
| `verified-with-differences` | Official page reached but the title, number or term MIT states differs from the record; the differences are listed under verified.expectation_mismatches. |
| `page-only` | Official page reached but its data.json could not be read, so only the page title was confirmed. |
| `unavailable` | The recorded URL did not resolve when last checked. |
| `pending-review` | Not yet checked against the live site. |

## Foundations

Shared knowledge layer for the three engineering domains: mathematics, physics, circuits, electronics, signals, computation and measurement, introduced progressively as engineering problems need them.

Also relevant (primary domain elsewhere): MIT 6.012, MIT 6.302, MIT 8.21.

### MIT 6.002 — Circuits and Electronics (Spring 2007)

| Field | Value |
| --- | --- |
| Official URL | <https://ocw.mit.edu/courses/6-002-circuits-and-electronics-spring-2007/> |
| Course number(s) | 6.002 |
| Teaching term | Spring 2007 |
| Level (MIT) | Undergraduate |
| Instructor(s) as listed | Prof. Anant Agarwal |
| AIPE priority | core |
| AIPE reference area | Electrical Circuits |
| Available public resources | Lecture Videos, Problem Sets, Exams |
| Main knowledge areas (AIPE tags) | lumped-circuit-abstraction, kcl-kvl-nodal-analysis, thevenin-norton-equivalents, digital-abstraction-logic-gates, mosfet-switch-models, nonlinear-and-small-signal-analysis, mosfet-amplifiers, first-and-second-order-transients, sinusoidal-steady-state-impedance, filters-and-frequency-response, op-amp-negative-feedback, energy-and-power-in-cmos, limits-of-lumped-abstraction, laboratory-measurement-practice |
| Relevant AIPE modules | `f.dc-circuits` (core), `f.electronics` (core), `f.dynamics` (core), `f.ac` (partial), `f.signals` (partial), `f.magnetism` (introductory), `pe.devices` (introductory), `pe.losses` (introductory) |
| Lessons citing this course | `buck-converter-fundamentals`, `dc-circuit-fundamentals`, `first-circuit-zh`, `three-phase-fundamentals` |
| Access limitations | Lecture notes and video for Fall 2000 lecture 24 ('Power conversion circuits and diodes') are stated as not available on the lecture-notes and video-gallery pages. The video-gallery page adds that resources from that se…; The lecture notes and videos are from the Fall 2000 offering, while the calendar, syllabus, assignments, labs and readings are Spring 2007. Of the 9 exam PDFs only Quiz 1, Quiz 2 and the Final are Spring 2007; the other…; Per the metadata-only policy no PDF (notes, homework, exams, labs, handouts), video or '( M )' file was opened, so topic coverage inside those files is inferred from titles only.; (+7 more in the JSON source) |
| Verification | verified on 2026-10-20 (HTTP 200; syllabus HTTP 200) |

Official resource pages (summaries in `references/mit-ocw-coverage.json`):

- [Course home page](https://ocw.mit.edu/courses/6-002-circuits-and-electronics-spring-2007/)
- [Syllabus](https://ocw.mit.edu/courses/6-002-circuits-and-electronics-spring-2007/pages/syllabus/)
- [Calendar](https://ocw.mit.edu/courses/6-002-circuits-and-electronics-spring-2007/pages/calendar/)
- [Lecture notes listing](https://ocw.mit.edu/courses/6-002-circuits-and-electronics-spring-2007/pages/lecture-notes/)
- [Video lectures gallery](https://ocw.mit.edu/courses/6-002-circuits-and-electronics-spring-2007/video_galleries/video-lectures/)
- [Assignments (problem sets)](https://ocw.mit.edu/courses/6-002-circuits-and-electronics-spring-2007/pages/assignments/)
- [Exams](https://ocw.mit.edu/courses/6-002-circuits-and-electronics-spring-2007/pages/exams/)
- [Labs listing](https://ocw.mit.edu/courses/6-002-circuits-and-electronics-spring-2007/pages/labs/)
- [Readings listing](https://ocw.mit.edu/courses/6-002-circuits-and-electronics-spring-2007/pages/readings/)
- [Tools](https://ocw.mit.edu/courses/6-002-circuits-and-electronics-spring-2007/pages/tools/)

Scope (AIPE summary in its own words):

MIT 6.002 (Spring 2007, Prof. Anant Agarwal; the home page states the course materials were created collaboratively with Prof. Jeffrey H. Lang) is MIT's first undergraduate circuits course, built on the lumped circuit abstraction. Over 25 lectures and 26 recitations it moves from resistive network analysis (KVL/KCL, node method, superposition, Thevenin/Norton) through the digital abstraction and MOSFET switch and amplifier models (large- and small-signal), into capacitors, inductors and first- and second-order transients, then sinusoidal steady state, impedance methods and filters, operational-amplifier feedback circuits, and energy and power in digital/CMOS circuits, ending with a lecture on the limits of the lumped abstraction. Five lab assignments (Lab 0 familiarization; Thevenin/Norton equivalents and logic gates; MOSFET amplifiers and first-order circuits; second-order networks; a…

### MIT 18.01SC — Single Variable Calculus (Fall 2010)

| Field | Value |
| --- | --- |
| Official URL | <https://ocw.mit.edu/courses/18-01sc-single-variable-calculus-fall-2010/> |
| Course number(s) | 18.01SC |
| Teaching term | Fall 2010 |
| Level (MIT) | Undergraduate |
| Instructor(s) as listed | Prof. David Jerison |
| AIPE priority | foundation |
| AIPE reference area | Calculus |
| Available public resources | Lecture Notes, Lecture Videos, Problem-solving Videos, Problem Sets, Problem Set Solutions, Exams, Exam Solutions |
| Main knowledge areas (AIPE tags) | single-variable-calculus, differentiation, definite-integral, fundamental-theorem-of-calculus, first-order-differential-equations, separation-of-variables, exponential-function, linear-approximation, optimization, numerical-integration, newtons-method, taylor-series, improper-integrals |
| Relevant AIPE modules | `f.calculus` (core), `f.computation` (introductory) |
| Lessons citing this course | `dc-circuit-fundamentals` |
| Access limitations | No calendar page exists: pages/calendar/ returns a 301 to resources/calendar/index.html, which never resolves to a 200 page (OCW Scholar courses are organised by session instead of a calendar).; The learning-resource-type listing pages live under lists/<type>/ (each redirecting to resources/<type>/index.html); they list PDF/video items by filename or clip title, not by lecture title, so topic titles were taken…; The course home page truncates several part titles in its navigation (e.g. '...Differential Equa', '...Com'); full part titles were read from the unit and part pages.; (+6 more in the JSON source) |
| Verification | verified on 2026-10-20 (HTTP 200; syllabus HTTP 200) |

Official resource pages (summaries in `references/mit-ocw-coverage.json`):

- [Syllabus](https://ocw.mit.edu/courses/18-01sc-single-variable-calculus-fall-2010/pages/syllabus/)
- [Course-home-and-unit-navigation](https://ocw.mit.edu/courses/18-01sc-single-variable-calculus-fall-2010/)
- [Lecture-notes-listing](https://ocw.mit.edu/courses/18-01sc-single-variable-calculus-fall-2010/lists/lecture-notes/)
- [Lecture-videos-listing](https://ocw.mit.edu/courses/18-01sc-single-variable-calculus-fall-2010/lists/lecture-videos/)
- [Problem-solving-videos-listing](https://ocw.mit.edu/courses/18-01sc-single-variable-calculus-fall-2010/lists/problem-solving-videos/)
- [Problem-sets-listing](https://ocw.mit.edu/courses/18-01sc-single-variable-calculus-fall-2010/lists/problem-sets/)
- [Problem-set-solutions-listing](https://ocw.mit.edu/courses/18-01sc-single-variable-calculus-fall-2010/lists/problem-set-solutions/)
- [Exams-listing](https://ocw.mit.edu/courses/18-01sc-single-variable-calculus-fall-2010/lists/exams/)
- [Exam-solutions-listing](https://ocw.mit.edu/courses/18-01sc-single-variable-calculus-fall-2010/lists/exam-solutions/)
- [Final-exam-page](https://ocw.mit.edu/courses/18-01sc-single-variable-calculus-fall-2010/pages/final-exam/)
- [Session-page-sample](https://ocw.mit.edu/courses/18-01sc-single-variable-calculus-fall-2010/pages/1.-differentiation/part-a-definition-and-basic-rules/session-1-introduction-to-derivatives/)
- [Session-page-numerical-integration](https://ocw.mit.edu/courses/18-01sc-single-variable-calculus-fall-2010/pages/unit-3-the-definite-integral-and-its-applications/part-c-average-value-probability-and-numerical-integration/session-63-numerical-integration/)
- [Session-page-inverse-functions](https://ocw.mit.edu/courses/18-01sc-single-variable-calculus-fall-2010/pages/1.-differentiation/part-b-implicit-differentiation-and-inverse-functions/session-15-implicit-differentiation-and-inverse-functions/)
- [Problem-set-page-sample](https://ocw.mit.edu/courses/18-01sc-single-variable-calculus-fall-2010/pages/unit-2-applications-of-differentiation/part-c-mean-value-theorem-antiderivatives-and-differential-equations/problem-set-5/)

Scope (AIPE summary in its own words):

MIT 18.01SC (OCW Scholar edition, Fall 2010, Prof. David Jerison) is a self-contained single-variable calculus course for independent learners. It runs through five units: differentiation (definition, rules, implicit differentiation, exponentials and inverses), applications of differentiation (approximation, curve sketching, optimization, related rates, Newton's method, Mean Value Theorem, antiderivatives and a first look at separable differential equations), the definite integral and its applications (Riemann sums, both Fundamental Theorems, areas, volumes, averages, probability, numerical integration), techniques of integration (trigonometric methods, partial fractions, integration by parts, arc length, parametric and polar curves), and infinite processes (L'Hospital's rule, improper integrals, series and Taylor series). The material is organised as 102 sequential sessions (Sessions 1…

### MIT 18.02SC — Multivariable Calculus (Fall 2010)

| Field | Value |
| --- | --- |
| Official URL | <https://ocw.mit.edu/courses/18-02sc-multivariable-calculus-fall-2010/> |
| Course number(s) | 18.02SC |
| Teaching term | Fall 2010 |
| Level (MIT) | Undergraduate |
| Instructor(s) as listed | Prof. Denis Auroux |
| AIPE priority | foundation |
| AIPE reference area | Advanced Mathematics |
| Available public resources | Lecture Videos, Lecture Notes, Problem Sets, Problem Set Solutions, Exams, Exam Solutions |
| Main knowledge areas (AIPE tags) | multivariable-calculus, vectors-and-matrices, linear-systems, partial-derivatives, gradient-and-chain-rule, linear-approximation, constrained-optimization, multiple-integrals, vector-fields, line-and-surface-integrals, divergence-and-stokes-theorems, diffusion-equation, maxwell-equations |
| Relevant AIPE modules | `f.calculus` (core), `f.linear-algebra` (partial) |
| Lessons citing this course | — |
| Access limitations | pages/calendar/ does not exist as a page for this OCW Scholar course: the request returned HTTP 301 to a resources/calendar/index.html path, which was not followed; sequencing evidence is the unit/part/session hierarchy…; There is no separate lecture-notes listing or video-gallery index page; video clips, notes PDFs and recitation videos are linked from the individual session pages (Session 1 sampled; the syllabus says most sessions incl…; PDFs, video files, Mathlets (Java applets) and the whole-course download were not opened; resource counts come from HTML link listings only.; (+2 more in the JSON source) |
| Verification | verified on 2026-10-20 (HTTP 200; syllabus HTTP 200) |

Official resource pages (summaries in `references/mit-ocw-coverage.json`):

- [Course-home](https://ocw.mit.edu/courses/18-02sc-multivariable-calculus-fall-2010/)
- [Syllabus](https://ocw.mit.edu/courses/18-02sc-multivariable-calculus-fall-2010/pages/syllabus/)
- [Unit-page](https://ocw.mit.edu/courses/18-02sc-multivariable-calculus-fall-2010/pages/1.-vectors-and-matrices/)
- [Unit-page](https://ocw.mit.edu/courses/18-02sc-multivariable-calculus-fall-2010/pages/2.-partial-derivatives/)
- [Unit-page](https://ocw.mit.edu/courses/18-02sc-multivariable-calculus-fall-2010/pages/3.-double-integrals-and-line-integrals-in-the-plane/)
- [Unit-page](https://ocw.mit.edu/courses/18-02sc-multivariable-calculus-fall-2010/pages/4.-triple-integrals-and-surface-integrals-in-3-space/)
- [Session-page-sample](https://ocw.mit.edu/courses/18-02sc-multivariable-calculus-fall-2010/pages/1.-vectors-and-matrices/part-a-vectors-determinants-and-planes/session-1-vectors/)
- [Problem-set-page-sample](https://ocw.mit.edu/courses/18-02sc-multivariable-calculus-fall-2010/pages/1.-vectors-and-matrices/part-a-vectors-determinants-and-planes/problem-set-1/)
- [Exam-page-sample](https://ocw.mit.edu/courses/18-02sc-multivariable-calculus-fall-2010/pages/1.-vectors-and-matrices/exam-1/exam/)
- [Final-exam-section](https://ocw.mit.edu/courses/18-02sc-multivariable-calculus-fall-2010/pages/final-exam-1/)
- [Download](https://ocw.mit.edu/courses/18-02sc-multivariable-calculus-fall-2010/download)

Scope (AIPE summary in its own words):

18.02SC is the OCW Scholar (self-study) edition of MIT's second-semester freshman calculus, taught by Prof. Denis Auroux: vector and matrix algebra, calculus of functions of several variables (partial derivatives, gradient, chain rule, optimisation with and without constraints), double and triple integrals in several coordinate systems, and vector calculus in two and three dimensions culminating in Green's, Stokes' and the divergence theorems, with a short physics-applications coda on Maxwell's equations. It is organised into 4 units, 12 parts and 102 numbered sessions, of which Sessions 22-23, 45-46 and 73 are unit-exam reviews and Sessions 99-102 are final-exam reviews. A typical session (Session 1 sampled) links a segmented lecture-video clip (recorded fall 2007) with board images, lecture notes, worked examples, a recitation video and problems with solutions; the syllabus says most…

### MIT 18.03SC — Differential Equations (Fall 2011)

| Field | Value |
| --- | --- |
| Official URL | <https://ocw.mit.edu/courses/18-03sc-differential-equations-fall-2011/> |
| Course number(s) | 18.03SC |
| Teaching term | Fall 2011 |
| Level (MIT) | Undergraduate |
| Instructor(s) as listed | Prof. Arthur Mattuck, Prof. Haynes Miller, Dr. Jeremy Orloff, Dr. John Lewis |
| AIPE priority | foundation |
| AIPE reference area | Dynamic Systems |
| Available public resources | Lecture Videos, Problem-solving Videos, Lecture Notes, Problem Sets, Problem Set Solutions, Exams, Exam Solutions |
| Main knowledge areas (AIPE tags) | ordinary-differential-equations, first-order-odes, second-order-linear-odes, numerical-ode-methods, complex-exponentials, sinusoidal-steady-state, laplace-transform, fourier-series, transfer-functions-and-poles, impulse-response-convolution, frequency-response-resonance, linear-systems-eigenvalues, phase-portraits-linearisation |
| Relevant AIPE modules | `f.calculus` (partial), `f.signals` (core), `f.dynamics` (partial), `f.linear-algebra` (partial), `f.ac` (partial), `f.computation` (introductory) |
| Lessons citing this course | — |
| Access limitations | No calendar page: pages/calendar/ returns 301 to resources/calendar/index.html, which itself returns 301 to the same URL (a redirect loop with no 200 page). This is consistent with a self-paced OCW Scholar course organi…; The standard pages/syllabus/ path returns 301 to resources/syllabus/index.html, which returns 301 to itself (no 200 page); the syllabus is served at pages/syllabus/syllabus/ (HTTP 200), which is why references/mit-ocw-v…; The video_galleries/ root returns 301 to resources/index.html, which returns 301 to itself (no 200 page); video listings are instead at pages/lecture-videos/ and pages/problem-solving-videos/ (both HTTP 200).; (+3 more in the JSON source) |
| Verification | verified on 2026-10-20 (HTTP 200; syllabus HTTP None) |

Official resource pages (summaries in `references/mit-ocw-coverage.json`):

- [Course home page](https://ocw.mit.edu/courses/18-03sc-differential-equations-fall-2011/)
- [Syllabus](https://ocw.mit.edu/courses/18-03sc-differential-equations-fall-2011/pages/syllabus/syllabus/)
- [Unit overview page](https://ocw.mit.edu/courses/18-03sc-differential-equations-fall-2011/pages/unit-i-first-order-differential-equations/)
- [Unit overview page](https://ocw.mit.edu/courses/18-03sc-differential-equations-fall-2011/pages/unit-ii-second-order-constant-coefficient-linear-equations/)
- [Unit overview page](https://ocw.mit.edu/courses/18-03sc-differential-equations-fall-2011/pages/unit-iii-fourier-series-and-laplace-transform/)
- [Unit overview page](https://ocw.mit.edu/courses/18-03sc-differential-equations-fall-2011/pages/unit-iv-first-order-systems/)
- [Session pages (39)](https://ocw.mit.edu/courses/18-03sc-differential-equations-fall-2011/pages/unit-i-first-order-differential-equations/conventions-and-preliminary-material/)
- [Lecture notes listing](https://ocw.mit.edu/courses/18-03sc-differential-equations-fall-2011/pages/lecture-notes/)
- [Lecture videos listing](https://ocw.mit.edu/courses/18-03sc-differential-equations-fall-2011/pages/lecture-videos/)
- [Problem-solving videos listing](https://ocw.mit.edu/courses/18-03sc-differential-equations-fall-2011/pages/problem-solving-videos/)
- [Problem sets listing](https://ocw.mit.edu/courses/18-03sc-differential-equations-fall-2011/pages/problem-sets/)
- [Problem set solutions listing](https://ocw.mit.edu/courses/18-03sc-differential-equations-fall-2011/pages/problem-set-solutions/)
- [Exams listing](https://ocw.mit.edu/courses/18-03sc-differential-equations-fall-2011/pages/exams/)
- [Exam solutions listing](https://ocw.mit.edu/courses/18-03sc-differential-equations-fall-2011/pages/exam-solutions/)
- [Unit exam pages](https://ocw.mit.edu/courses/18-03sc-differential-equations-fall-2011/pages/unit-i-first-order-differential-equations/exam-1/)
- [Final exam page](https://ocw.mit.edu/courses/18-03sc-differential-equations-fall-2011/pages/final-exam/)

Scope (AIPE summary in its own words):

18.03SC is the OCW Scholar self-study edition of MIT's undergraduate differential-equations course. It is built from four units: first-order ODEs (analytic, geometric and numerical methods, complex arithmetic, sinusoidal and exponential inputs, autonomous equations), second-order constant-coefficient linear equations (characteristic equation, damped oscillators, exponential response, gain and phase lag, resonance, frequency response, an LRC-circuit application), Fourier series and Laplace transform (periodic input, step and delta functions, impulse response, convolution, transfer functions, poles), and first-order 2x2 systems (matrix methods, eigenvalues, phase portraits, matrix exponentials, linearisation of nonlinear systems, limit cycles and chaos). The navigation lists 39 session pages plus three unit exams and a final. Most session pages link course-note PDFs, clips from Prof. Matt…

### MIT 18.06SC — Linear Algebra (Fall 2011)

| Field | Value |
| --- | --- |
| Official URL | <https://ocw.mit.edu/courses/18-06sc-linear-algebra-fall-2011/> |
| Course number(s) | 18.06SC |
| Teaching term | Fall 2011 |
| Level (MIT) | Undergraduate |
| Instructor(s) as listed | Prof. Gilbert Strang |
| AIPE priority | foundation |
| AIPE reference area | Linear Systems and Modelling |
| Available public resources | Lecture Videos, Lecture Notes, Problem-solving Videos, Instructor Insights, Problem Sets, Problem Set Solutions, Exams, Exam Solutions |
| Main knowledge areas (AIPE tags) | linear-algebra, systems-of-linear-equations, matrix-factorization, vector-spaces-and-rank, orthogonality-and-least-squares, determinants, eigenvalues-and-eigenvectors, matrix-exponential-and-state-space, symmetric-and-positive-definite-matrices, singular-value-decomposition, incidence-matrices-and-networks, linear-transformations-and-change-of-basis, complex-matrices-fourier-series-and-fft |
| Relevant AIPE modules | `f.linear-algebra` (core), `f.signals` (introductory) |
| Lessons citing this course | — |
| Access limitations | pages/calendar/ is not retrievable: it answers HTTP 301 to resources/calendar/index.html, which itself answers HTTP 301 to the same URL (redirect loop, checked 2026-10-20); this OCW Scholar course has no readable calend…; Lecture notes exist only as per-session 'lecture summary' PDFs; problem sets, solutions and exams are PDFs; none were opened (metadata only).; Lecture and recitation videos were not viewed; only their titles as listed on HTML pages are recorded.; (+4 more in the JSON source) |
| Verification | verified on 2026-10-20 (HTTP 200; syllabus HTTP 200) |

Official resource pages (summaries in `references/mit-ocw-coverage.json`):

- [Course-home](https://ocw.mit.edu/courses/18-06sc-linear-algebra-fall-2011/)
- [Syllabus](https://ocw.mit.edu/courses/18-06sc-linear-algebra-fall-2011/pages/syllabus/)
- [Unit-listing](https://ocw.mit.edu/courses/18-06sc-linear-algebra-fall-2011/pages/ax-b-and-the-four-subspaces/)
- [Unit-listing](https://ocw.mit.edu/courses/18-06sc-linear-algebra-fall-2011/pages/least-squares-determinants-and-eigenvalues/)
- [Unit-listing](https://ocw.mit.edu/courses/18-06sc-linear-algebra-fall-2011/pages/positive-definite-matrices-and-applications/)
- [Resource-index](https://ocw.mit.edu/courses/18-06sc-linear-algebra-fall-2011/pages/resource-index/)
- [Session-page](https://ocw.mit.edu/courses/18-06sc-linear-algebra-fall-2011/pages/ax-b-and-the-four-subspaces/the-geometry-of-linear-equations/)
- [Session-page](https://ocw.mit.edu/courses/18-06sc-linear-algebra-fall-2011/pages/ax-b-and-the-four-subspaces/graphs-networks-incidence-matrices/)
- [Session-page](https://ocw.mit.edu/courses/18-06sc-linear-algebra-fall-2011/pages/least-squares-determinants-and-eigenvalues/differential-equations-and-exp-at/)
- [Session-page](https://ocw.mit.edu/courses/18-06sc-linear-algebra-fall-2011/pages/least-squares-determinants-and-eigenvalues/projection-matrices-and-least-squares/)
- [Session-page](https://ocw.mit.edu/courses/18-06sc-linear-algebra-fall-2011/pages/positive-definite-matrices-and-applications/singular-value-decomposition/)
- [Exam-page](https://ocw.mit.edu/courses/18-06sc-linear-algebra-fall-2011/pages/ax-b-and-the-four-subspaces/exam-1/)
- [Final-review](https://ocw.mit.edu/courses/18-06sc-linear-algebra-fall-2011/pages/final-course-review/)
- [Final-exam](https://ocw.mit.edu/courses/18-06sc-linear-algebra-fall-2011/pages/final-exam/)
- [Instructor-insights](https://ocw.mit.edu/courses/18-06sc-linear-algebra-fall-2011/pages/instructor-insights/)
- [Related-resources](https://ocw.mit.edu/courses/18-06sc-linear-algebra-fall-2011/pages/related-resources/)
- [Supplementary-video](https://ocw.mit.edu/courses/18-06sc-linear-algebra-fall-2011/pages/final-1806-lecture-2023/)
- [Download](https://ocw.mit.edu/courses/18-06sc-linear-algebra-fall-2011/download/)

Scope (AIPE summary in its own words):

18.06SC is the OCW Scholar self-study version of MIT's undergraduate linear algebra course (Prof. Gilbert Strang, Fall 2011), organised in three units: (I) solving Ax = b, elimination, LU, inverses and the four fundamental subspaces; (II) orthogonality, projections and least squares, determinants, eigenvalues, diagonalization and the matrix exponential exp(At) for systems of differential equations, Markov matrices and Fourier series; (III) symmetric and positive definite matrices, complex matrices and the FFT, similar matrices and Jordan form, SVD, linear transformations, change of basis and pseudoinverses. Each lecture session pairs a lecture video with a lecture-summary PDF, suggested textbook sections and a recitation (problem-solving) video; 31 of the 36 lecture sessions also carry a problem set with solutions (the overview session, the three exam-review sessions and the final revie…

### MIT 6.003 — Signals and Systems (Fall 2011)

| Field | Value |
| --- | --- |
| Official URL | <https://ocw.mit.edu/courses/6-003-signals-and-systems-fall-2011/> |
| Course number(s) | 6.003 |
| Teaching term | Fall 2011 |
| Level (MIT) | Undergraduate |
| Instructor(s) as listed | Prof. Dennis Freeman |
| AIPE priority | foundation |
| AIPE reference area | Signals and Control Foundations |
| Available public resources | Lecture Videos, Lecture Notes, Problem Sets, Problem Set Solutions, Exams, Exam Solutions |
| Main knowledge areas (AIPE tags) | signals-and-systems, lti-systems, discrete-time-systems, z-transform, laplace-transform, convolution, frequency-response, bode-plots, feedback-control, fourier-analysis, sampling-and-quantization, modulation |
| Relevant AIPE modules | `f.signals` (core), `pe.control` (introductory), `f.computation` (introductory), `f.magnetism` (introductory) |
| Lessons citing this course | — |
| Access limitations | All eight HTML pages returned HTTP 200 on 2026-10-20; six of them (home page, syllabus, calendar, lecture-notes listing, readings, video gallery index) were re-fetched during finalisation and all titles recorded here we…; Lecture-note PDFs (25), problem-set and solution PDFs (28), exam PDFs (22), the supplementary-notes PDFs (11), the image files attached to problem sets 5 and 11, the course download ZIP and the lecture videos were delib…; The video gallery index lists titles only; individual video pages (and any transcripts) were not opened, so video durations and contents are unknown; (+3 more in the JSON source) |
| Verification | verified on 2026-10-20 (HTTP 200; syllabus HTTP 200) |

Official resource pages (summaries in `references/mit-ocw-coverage.json`):

- [Course home page](https://ocw.mit.edu/courses/6-003-signals-and-systems-fall-2011/)
- [Syllabus](https://ocw.mit.edu/courses/6-003-signals-and-systems-fall-2011/pages/syllabus/)
- [Calendar](https://ocw.mit.edu/courses/6-003-signals-and-systems-fall-2011/pages/calendar/)
- [Lecture notes listing](https://ocw.mit.edu/courses/6-003-signals-and-systems-fall-2011/pages/lecture-notes/)
- [Lecture video gallery index](https://ocw.mit.edu/courses/6-003-signals-and-systems-fall-2011/video_galleries/lecture-videos/)
- [Assignments listing](https://ocw.mit.edu/courses/6-003-signals-and-systems-fall-2011/pages/assignments/)
- [Readings](https://ocw.mit.edu/courses/6-003-signals-and-systems-fall-2011/pages/readings/)
- [Exams listing](https://ocw.mit.edu/courses/6-003-signals-and-systems-fall-2011/pages/exams/)

Scope (AIPE summary in its own words):

MIT 6.003 Signals and Systems (Fall 2011, undergraduate, Prof. Dennis Freeman) is a one-semester course in signal and LTI-system analysis that develops the discrete-time and continuous-time cases side by side. The syllabus groups the material into two strands: ways of representing signals (singularity functions, complex exponentials, the Fourier, Laplace and Z transforms, and sampling) and ways of representing linear time-invariant systems (block diagrams, difference or differential equations, system functions with their poles and zeros, convolution sums and integrals, and the impulse, step and frequency responses). The 25 lecture titles run from DT and CT systems through the Z and Laplace transforms, convolution, frequency response, Bode plots and feedback/control to the four Fourier representations, sampling and quantization, modulation and an Audio CD capstone; MIT names control, com…

### MIT 8.02 — Physics II: Electricity and Magnetism (Spring 2007)

| Field | Value |
| --- | --- |
| Official URL | <https://ocw.mit.edu/courses/8-02-physics-ii-electricity-and-magnetism-spring-2007/> |
| Course number(s) | 8.02 |
| Teaching term | Spring 2007 |
| Level (MIT) | Undergraduate |
| Instructor(s) as listed | Physics Department Faculty, Lecturers, and Technical Staff |
| AIPE priority | foundation |
| AIPE reference area | Electromagnetics |
| Available public resources | Problem Sets, Lecture Notes |
| Main knowledge areas (AIPE tags) | electrostatics, electric-potential, gauss-law, capacitance-dielectrics, dc-circuits, magnetostatics, biot-savart-ampere, faraday-induction, inductance-transformers, rc-rl-rlc-transients, ac-resonance-phasors, maxwell-equations-em-waves |
| Relevant AIPE modules | `f.electromagnetism` (core), `f.dynamics` (partial), `f.ac` (partial), `f.magnetism` (partial), `f.dc-circuits` (introductory), `ps.transformers` (introductory), `ps.machines` (introductory) |
| Lessons citing this course | `dc-circuit-fundamentals` |
| Access limitations | No calendar page: pages/calendar/ answers HTTP 301 into a self-referencing redirect loop at resources/calendar/index.html (curl stops at the redirect limit, exit 47) and the course menu has no Calendar entry; the schedu…; pages/assignments/ and pages/exams/ behave the same way (301 redirect loop, not in the menu); problem sets live under Problem Solving, and sessions 13, 24 and 34 are only 'Exam N information' sessions with no exam page.; No lecture videos: pages/video-lectures/ and pages/lecture-videos/ are the same redirect loop and the menu lists no video section; the Lecture Notes resource listing (resources/lecture-notes/index.html) shows 25 slide P…; (+4 more in the JSON source) |
| Verification | verified on 2026-10-20 (HTTP 200; syllabus HTTP 200) |

Official resource pages (summaries in `references/mit-ocw-coverage.json`):

- [Course home page](https://ocw.mit.edu/courses/8-02-physics-ii-electricity-and-magnetism-spring-2007/)
- [Syllabus](https://ocw.mit.edu/courses/8-02-physics-ii-electricity-and-magnetism-spring-2007/pages/syllabus/)
- [Class topics schedule](https://ocw.mit.edu/courses/8-02-physics-ii-electricity-and-magnetism-spring-2007/pages/class-topics/)
- [Readings listing](https://ocw.mit.edu/courses/8-02-physics-ii-electricity-and-magnetism-spring-2007/pages/readings/)
- [Class activities schedule](https://ocw.mit.edu/courses/8-02-physics-ii-electricity-and-magnetism-spring-2007/pages/class-activities/)
- [Lecture notes (class slides)](https://ocw.mit.edu/courses/8-02-physics-ii-electricity-and-magnetism-spring-2007/pages/class-slides/)
- [Lecture notes resource listing](https://ocw.mit.edu/courses/8-02-physics-ii-electricity-and-magnetism-spring-2007/resources/lecture-notes/index.html)
- [Problem sets](https://ocw.mit.edu/courses/8-02-physics-ii-electricity-and-magnetism-spring-2007/pages/problem-solving/)
- [Experiments](https://ocw.mit.edu/courses/8-02-physics-ii-electricity-and-magnetism-spring-2007/pages/experiments/)

Scope (AIPE summary in its own words):

MIT 8.02 (Spring 2007) is MIT's first-year electricity-and-magnetism course, the second half of the introductory physics sequence. It is run in the TEAL studio format: short lecture segments alternate with tabletop experiments, electronically polled concept questions and small-group problem work, and one one-hour session a week is given over to problem solving. Its 36 sessions (26 marked Class and 10 marked Problem solving in the Class Topics table) run from electrostatics (charge, field, potential, Gauss's law, conductors and capacitors) through current and DC circuits, magnetostatics (Biot-Savart, Ampere's law, forces and torques on charges, dipoles and current loops), Faraday's law, inductance and transformers, RC/RL/RLC transients and driven AC resonance, to Maxwell's equations, electromagnetic radiation and a closing session on interference. The OCW site offers lecture notes (14 co…

### MIT 6.013 — Electromagnetics and Applications (Fall 2005)

| Field | Value |
| --- | --- |
| Official URL | <https://ocw.mit.edu/courses/6-013-electromagnetics-and-applications-fall-2005/> |
| Course number(s) | 6.013, ESD.013J |
| Teaching term | Fall 2005 |
| Level (MIT) | Undergraduate |
| Instructor(s) as listed | Prof. David Staelin, Prof. Erich Ippen, Markus Zahn |
| AIPE priority | supplementary |
| AIPE reference area | Applied Electromagnetics |
| Available public resources | Lecture Notes, Problem Sets, Problem Set Solutions, Exams, Exam Solutions |
| Main knowledge areas (AIPE tags) | maxwell-equations, quasistatics, electrostatics-and-potential, dielectric-conducting-magnetic-media, plane-waves, transmission-lines, smith-chart, waveguides-and-resonators, field-energy-and-forces, magnetic-circuits, rotating-machines, antennas-and-radiation |
| Relevant AIPE modules | `f.electromagnetism` (core), `f.magnetism` (partial), `ps.machines` (partial), `ps.components` (introductory), `f.dynamics` (introductory) |
| Lessons citing this course | — |
| Access limitations | No lecture videos are published for this course; the resource types listed are lecture notes, problem sets with solutions, and exams with solutions only.; All substantive material (20 lecture-note PDFs, 11 problem sets and 11 solution PDFs, 2 quizzes and 2 solution PDFs, 3 formula-sheet PDFs) is in PDF files that were not opened; only listing titles and counts were record…; The required text is the instructor's own course notes, referenced on the readings page by section numbers only and not published as a file on these pages; the Haus/Melcher text is described as out of print and is linke…; (+6 more in the JSON source) |
| Verification | verified on 2026-10-20 (HTTP 200; syllabus HTTP 200) |

Official resource pages (summaries in `references/mit-ocw-coverage.json`):

- [Course home page](https://ocw.mit.edu/courses/6-013-electromagnetics-and-applications-fall-2005/)
- [Syllabus](https://ocw.mit.edu/courses/6-013-electromagnetics-and-applications-fall-2005/pages/syllabus/)
- [Calendar](https://ocw.mit.edu/courses/6-013-electromagnetics-and-applications-fall-2005/pages/calendar/)
- [Lecture notes listing](https://ocw.mit.edu/courses/6-013-electromagnetics-and-applications-fall-2005/pages/lecture-notes/)
- [Readings](https://ocw.mit.edu/courses/6-013-electromagnetics-and-applications-fall-2005/pages/readings/)
- [Problem sets](https://ocw.mit.edu/courses/6-013-electromagnetics-and-applications-fall-2005/pages/assignments/)
- [Exams](https://ocw.mit.edu/courses/6-013-electromagnetics-and-applications-fall-2005/pages/exams/)
- [Study materials](https://ocw.mit.edu/courses/6-013-electromagnetics-and-applications-fall-2005/pages/study-materials/)
- [Related resources](https://ocw.mit.edu/courses/6-013-electromagnetics-and-applications-fall-2005/pages/related-resources/)
- [Course download](https://ocw.mit.edu/courses/6-013-electromagnetics-and-applications-fall-2005/download/)

Scope (AIPE summary in its own words):

MIT 6.013 (Fall 2005, undergraduate; listed under Electrical Engineering and Computer Science and the Engineering Systems Division; instructors listed as Prof. David Staelin, Prof. Erich Ippen and Markus Zahn) is an applied electromagnetics course that builds Maxwell's equations from the Coulomb-Lorentz force law, through boundary conditions, potentials, media and the electro-/magneto-quasistatic approximations, and then applies them in six units: Maxwell's equations, plane waves, transmission lines and waveguides, fields and forces (field energy, virtual-work forces, rotating and self-excited machines), antennas and radiation, and acoustics. The course page names applications spanning wireless and optical communications, circuits and computer interconnects, microwave links and radar, sensors, MEMS, motors, and power generation and transmission. Delivery was 23 lectures and 25 recitatio…

## Power Electronics

Switching devices, converter topologies, losses, modelling, control, magnetics and the practical constraints of real converters.

Also relevant (primary domain elsewhere): MIT 6.002, MIT 6.003, MIT 6.013.

### MIT 6.622 — Power Electronics (Spring 2023)

| Field | Value |
| --- | --- |
| Official URL | <https://ocw.mit.edu/courses/6-622-power-electronics-spring-2023/> |
| Course number(s) | 6.622, 6.6220 |
| Teaching term | Spring 2023 |
| Level (MIT) | Graduate |
| Instructor(s) as listed | Prof. David Perreault |
| AIPE priority | core |
| AIPE reference area | Principal power electronics benchmark |
| Available public resources | Lecture Videos, Lecture Notes, Design Assignments, Problem Sets, Problem Set Solutions, Exams, Exam Solutions |
| Main knowledge areas (AIPE tags) | power-electronics, dc-dc-converters, rectifiers-and-power-factor, switched-mode-rectifiers, magnetics-design, isolated-converters, inverters, three-phase-systems, converter-modelling-and-control, switching-losses-and-thermal, emi-filters, soft-switching-and-resonant, switched-capacitor-converters, gate-drive-and-layout |
| Relevant AIPE modules | `pe.topologies` (core), `pe.buck` (core), `pe.boost` (core), `pe.rectifiers` (core), `pe.inverters` (core), `pe.magnetics` (core), `pe.isolated` (core), `pe.resonant` (core), `pe.losses` (partial), `pe.thermal` (partial), `pe.modelling` (core), `pe.control` (core), `pe.emi-pcb` (core), `pe.practical` (partial), `pe.gate-driving` (introductory), `pe.passives` (partial), `pe.devices` (introductory), `pe.applications` (introductory), `ps.three-phase` (partial) |
| Lessons citing this course | `buck-converter`, `buck-converter-fundamentals`, `buck-open-lab` |
| Access limitations | pages/calendar/ is not published: on 2026-10-20 it returned HTTP 301 to .../resources/calendar/index.html, which returns HTTP 301 to itself; curl -L stopped at the redirect limit (exit code 47) with a 0-byte body on eve…; Lecture-note PDFs, videos, problem sets, assessments and the project-description PDF were not opened (licensing rule: HTML listing pages only), so the mapping rests on the 38 lecture titles, the syllabus text and the de…; The home-page menu has no Readings section and the syllabus gives no per-lecture reading list; only one textbook is cited.; (+5 more in the JSON source) |
| Verification | verified on 2026-10-20 (HTTP 200; syllabus HTTP 200) |

Official resource pages (summaries in `references/mit-ocw-coverage.json`):

- [Course home page](https://ocw.mit.edu/courses/6-622-power-electronics-spring-2023/)
- [Syllabus](https://ocw.mit.edu/courses/6-622-power-electronics-spring-2023/pages/syllabus/)
- [Lecture notes index](https://ocw.mit.edu/courses/6-622-power-electronics-spring-2023/pages/lecture-notes/)
- [Lecture notes (handwritten)](https://ocw.mit.edu/courses/6-622-power-electronics-spring-2023/lists/handwritten-lecture-notes/)
- [Lecture notes (typed)](https://ocw.mit.edu/courses/6-622-power-electronics-spring-2023/lists/typed-lecture-notes/)
- [Lecture videos](https://ocw.mit.edu/courses/6-622-power-electronics-spring-2023/video_galleries/video-lectures/)
- [Problem sets](https://ocw.mit.edu/courses/6-622-power-electronics-spring-2023/lists/problem-sets/)
- [Assessments (replace exams)](https://ocw.mit.edu/courses/6-622-power-electronics-spring-2023/lists/assessments/)
- [Design project](https://ocw.mit.edu/courses/6-622-power-electronics-spring-2023/pages/design-project/)
- [Course download](https://ocw.mit.edu/courses/6-622-power-electronics-spring-2023/download)

Scope (AIPE summary in its own words):

MIT 6.622 Power Electronics, Spring 2023, is a graduate subject taught by Prof. David Perreault on the modelling, analysis, design and control of switching circuits that convert electrical energy. Its 38 numbered lectures open with rectifiers, load regulation and power factor, continue with a four-lecture DC/DC block (inferred to be the non-isolated converter family, since isolated converters follow the magnetics block), four magnetics lectures, two lectures on isolated DC/DC converters, switching losses and snubbers, and thermal modelling and heat sinking; the second half covers a three-lecture inverter block, switched-mode rectifiers, three-phase systems and three-phase inverters, converter control including current-mode control, EMI filters (including common-mode and differential-mode noise), switched-capacitor converters, soft switching, resonant power conversion with matching netwo…

### MIT 6.012 — Microelectronic Devices and Circuits (Fall 2005)

| Field | Value |
| --- | --- |
| Official URL | <https://ocw.mit.edu/courses/6-012-microelectronic-devices-and-circuits-fall-2005/> |
| Course number(s) | 6.012 |
| Teaching term | Fall 2005 |
| Level (MIT) | Undergraduate |
| Instructor(s) as listed | Prof. Jesús del Alamo |
| AIPE priority | supplementary |
| AIPE reference area | Device foundations |
| Available public resources | Exams, Lecture Notes, Projects, Problem Sets |
| Main knowledge areas (AIPE tags) | semiconductor-physics, semiconductor-electrostatics, pn-junction, mosfet-physics, mos-capacitance, diode-charge-storage, bjt, cmos-inverter, large-signal-models, small-signal-models, device-equivalent-circuits, amplifier-frequency-response, spice-device-models |
| Relevant AIPE modules | `f.electronics` (core), `pe.devices` (partial), `pe.modelling` (partial), `f.signals` (partial), `f.electromagnetism` (partial), `pe.losses` (introductory), `pe.simulation` (introductory) |
| Lessons citing this course | `solar-pv-fundamentals` |
| Access limitations | No lecture videos exist for this course: the learning resource types are Exams, Lecture Notes, Problem Sets and Projects only, so topic evidence comes from the calendar and lecture-notes listing pages, not from recorded…; All lecture notes (26 + 24 annotated), 10 problem sets, 6 exam/solution files, the project brief, 3 OCW-hosted Cadence support files and 8 study-material files are PDFs; per the licensing rules none were opened, so this…; The MIT Microelectronics WebLab (Tools page) requires registration and is described as available to MIT students and collaborating institutions; AIPE learners cannot rely on it.; (+4 more in the JSON source) |
| Verification | verified on 2026-10-20 (HTTP 200; syllabus HTTP 200) |

Official resource pages (summaries in `references/mit-ocw-coverage.json`):

- [Course home](https://ocw.mit.edu/courses/6-012-microelectronic-devices-and-circuits-fall-2005/)
- [Syllabus](https://ocw.mit.edu/courses/6-012-microelectronic-devices-and-circuits-fall-2005/pages/syllabus/)
- [Calendar](https://ocw.mit.edu/courses/6-012-microelectronic-devices-and-circuits-fall-2005/pages/calendar/)
- [Lecture notes](https://ocw.mit.edu/courses/6-012-microelectronic-devices-and-circuits-fall-2005/pages/lecture-notes/)
- [Problem sets](https://ocw.mit.edu/courses/6-012-microelectronic-devices-and-circuits-fall-2005/pages/assignments/)
- [Exams](https://ocw.mit.edu/courses/6-012-microelectronic-devices-and-circuits-fall-2005/pages/exams/)
- [Projects](https://ocw.mit.edu/courses/6-012-microelectronic-devices-and-circuits-fall-2005/pages/projects/)
- [Study materials](https://ocw.mit.edu/courses/6-012-microelectronic-devices-and-circuits-fall-2005/pages/study-materials/)
- [Readings](https://ocw.mit.edu/courses/6-012-microelectronic-devices-and-circuits-fall-2005/pages/readings/)
- [Tools](https://ocw.mit.edu/courses/6-012-microelectronic-devices-and-circuits-fall-2005/pages/tools/)

Scope (AIPE summary in its own words):

MIT presents 6.012 Microelectronic Devices and Circuits (Fall 2005, undergraduate, Prof. Jesús del Alamo) as the entry course for its EECS devices/circuits/systems concentration. It starts from semiconductor carrier physics (electron and hole populations, doping with donors and acceptors, drift and diffusion), builds the electrostatics of p-n junctions and MOS structures, derives MOSFET current-voltage characteristics and equivalent-circuit (large-signal and small-signal) models, then applies them to NMOS/CMOS inverter logic (transfer characteristics, delay, scaling, dynamic power). A second device block covers p-n diode I-V, charge storage and diffusion capacitance, and the bipolar junction transistor; the final block treats MOSFET and BJT single-stage and multistage amplifiers, current sources and sinks, and amplifier frequency response (Miller effect, open-circuit time constants). As…

### MIT 6.302 — Feedback Systems (Spring 2007)

| Field | Value |
| --- | --- |
| Official URL | <https://ocw.mit.edu/courses/6-302-feedback-systems-spring-2007/> |
| Course number(s) | 6.302 |
| Teaching term | Spring 2007 |
| Level (MIT) | Graduate |
| Instructor(s) as listed | James Roberge, Prof. Joel Dawson, Dr. Kent Lundberg |
| AIPE priority | supplementary |
| AIPE reference area | Modelling and control |
| Available public resources | Problem Sets, Exams |
| Main knowledge areas (AIPE tags) | feedback-control, classical-control, stability-analysis, root-locus, nyquist-criterion, bode-plots-gain-phase-margin, steady-state-error, loop-compensation, minor-loop-compensation, op-amp-compensation, linearization, phase-locked-loops, describing-functions, servomotor-control |
| Relevant AIPE modules | `pe.control` (core), `f.signals` (partial), `pe.modelling` (partial), `ps.grid-converters` (introductory) |
| Lessons citing this course | — |
| Access limitations | No lecture notes are published for this course: the course menu has no Lecture Notes or Readings section, and the syllabus states that the course reference text (Lundberg's notes) is not available on OCW. Lecture conten…; No lecture videos of the 2007 offering exist; the Video Resources page only points to the separate OCW resource RES.6-010 (1985 Roberge lectures, 20 videos), which is a condensed earlier version of the subject, not a re…; Recitation handouts are missing for R21 (Block diagrams from circuits) and R22 (Return ratio); the page says these recitations were given by teaching assistants.; (+5 more in the JSON source) |
| Verification | verified on 2026-10-20 (HTTP 200; syllabus HTTP 200) |

Official resource pages (summaries in `references/mit-ocw-coverage.json`):

- [Course home page](https://ocw.mit.edu/courses/6-302-feedback-systems-spring-2007/)
- [Syllabus](https://ocw.mit.edu/courses/6-302-feedback-systems-spring-2007/pages/syllabus/)
- [Calendar](https://ocw.mit.edu/courses/6-302-feedback-systems-spring-2007/pages/calendar/)
- [Recitation handouts listing](https://ocw.mit.edu/courses/6-302-feedback-systems-spring-2007/pages/recitations/)
- [Labs listing](https://ocw.mit.edu/courses/6-302-feedback-systems-spring-2007/pages/labs/)
- [Problem sets listing](https://ocw.mit.edu/courses/6-302-feedback-systems-spring-2007/pages/assignments/)
- [Exams listing](https://ocw.mit.edu/courses/6-302-feedback-systems-spring-2007/pages/exams/)
- [Tools (software demos)](https://ocw.mit.edu/courses/6-302-feedback-systems-spring-2007/pages/tools/)
- [Video resources (pointer page)](https://ocw.mit.edu/courses/6-302-feedback-systems-spring-2007/pages/video-resources/)
- [Linked supplemental video gallery (separate ocw resource res.6-010)](https://ocw.mit.edu/courses/res-6-010-electronic-feedback-systems-spring-2013/video_galleries/course-videos)
- [Course download page](https://ocw.mit.edu/courses/6-302-feedback-systems-spring-2007/download)

Scope (AIPE summary in its own words):

MIT 6.302 Feedback Systems (Spring 2007, listed by OCW as Graduate; instructors James Roberge, Joel Dawson, Kent Lundberg) is an introductory feedback-control design course that this record characterises as classical and continuous-time (the record's own terms; no OCW page uses either). Judging from the session titles, it moves from the properties of feedback (desensitivity, linearisation), plant modelling and first/second-order dynamics, through stability tools (root locus, Nyquist criterion, Hall/Nichols charts, Bode gain and phase margins) to compensation design (lead/lag series compensation, minor-loop compensation, internal and external op-amp compensation, lightly damped plants) and finally nonlinear topics (describing functions, oscillators, conditional stability). Physical applications run through a servomotor laboratory (Lab 1A-1D) and a design project chosen from three options…

### MIT 6.334 — Power Electronics (Spring 2007)

| Field | Value |
| --- | --- |
| Official URL | <https://ocw.mit.edu/courses/6-334-power-electronics-spring-2007/> |
| Course number(s) | 6.334 |
| Teaching term | Spring 2007 |
| Level (MIT) | Graduate |
| Instructor(s) as listed | Prof. David Perreault |
| AIPE priority | historical |
| AIPE reference area | Historical / supplementary power electronics |
| Available public resources | Problem Sets, Lecture Notes |
| Main knowledge areas (AIPE tags) | dc-dc-converters, rectifiers-and-power-factor, distortion-and-harmonics, magnetics-design, isolated-converters, inverters-and-pwm, emi-filtering, switching-losses-and-snubbers, soft-switching-and-resonant-converters, converter-modelling-and-control, three-phase-rectifier-systems, thermal-design |
| Relevant AIPE modules | `pe.topologies` (core), `pe.buck` (partial), `pe.boost` (partial), `pe.rectifiers` (core), `pe.inverters` (core), `pe.magnetics` (core), `pe.isolated` (core), `pe.modelling` (core), `pe.control` (partial), `pe.resonant` (core), `pe.losses` (partial), `pe.thermal` (partial), `pe.emi-pcb` (partial), `pe.gate-driving` (introductory), `pe.practical` (partial), `pe.devices` (partial), `pe.passives` (introductory), `pe.simulation` (introductory), `pe.applications` (introductory), `ps.three-phase` (introductory), `ps.transformers` (introductory), `f.magnetism` (introductory) |
| Lessons citing this course | `buck-converter`, `buck-converter-fundamentals` |
| Access limitations | No lecture videos: the course lists only Lecture Notes and Problem Sets as learning-resource types, so there is no video gallery to cite.; The lecture-notes page lists 16 chapter PDFs that do not map one-to-one onto the 37 calendar lectures (chapter numbering differs from lecture numbering). Only 8 chapter titles are included in topic_outline because of th…; No quiz, practice-exam or exam-solutions page is published, although the syllabus and calendar mention two quizzes, quiz review sessions and practice exams.; (+7 more in the JSON source) |
| Verification | verified on 2026-10-20 (HTTP 200; syllabus HTTP 200) |

Official resource pages (summaries in `references/mit-ocw-coverage.json`):

- [Course-home](https://ocw.mit.edu/courses/6-334-power-electronics-spring-2007/)
- [Syllabus](https://ocw.mit.edu/courses/6-334-power-electronics-spring-2007/pages/syllabus/)
- [Calendar](https://ocw.mit.edu/courses/6-334-power-electronics-spring-2007/pages/calendar/)
- [Lecture-notes](https://ocw.mit.edu/courses/6-334-power-electronics-spring-2007/pages/lecture-notes/)
- [Problem-sets](https://ocw.mit.edu/courses/6-334-power-electronics-spring-2007/pages/assignments/)
- [Related-resources](https://ocw.mit.edu/courses/6-334-power-electronics-spring-2007/pages/related-resources/)
- [Download](https://ocw.mit.edu/courses/6-334-power-electronics-spring-2007/download)

Scope (AIPE summary in its own words):

MIT 6.334 Power Electronics (Spring 2007, graduate, Prof. David Perreault) is a one-semester graduate course on using electronic circuits for energy conversion and control, worth 6 engineering design points. Its 37 calendar lectures run from analysis methods and rectifier basics (AC-side reactance, power factor and distortion) through DC-DC converters, magnetics, isolated DC/DC converters, DC-AC inverters and PWM, EMI filtering, loss computation and snubbers, soft switching, thermal design and resonant/RF converters, to averaged modelling and control, three-phase (multi-pulse) rectifier systems, practical layout and gate-drive issues, switched-mode rectifiers and a closing design example. Assessment is weekly problem sets (40%), two evening quizzes (50%, no final exam) and a design project (10%); the required text is Kassakian, Schlecht and Verghese, Principles of Power Electronics, and…

## Power Systems

Three-phase networks, transformers and machines, per-unit analysis, power flow, faults and protection, stability, and converter-dominated modern grids.

Also relevant (primary domain elsewhere): MIT 6.013, MIT 6.302, MIT 22.081J, MIT 15.031J.

### MIT 6.061 — Introduction to Electric Power Systems (Spring 2011)

| Field | Value |
| --- | --- |
| Official URL | <https://ocw.mit.edu/courses/6-061-introduction-to-electric-power-systems-spring-2011/> |
| Course number(s) | 6.061, 6.690 |
| Teaching term | Spring 2011 |
| Level (MIT) | Undergraduate |
| Instructor(s) as listed | Prof. James L. Kirtley Jr. |
| AIPE priority | core |
| AIPE reference area | Foundational power systems |
| Available public resources | Problem Sets, Problem Set Solutions, Exams, Exam Solutions, Open Textbooks |
| Main knowledge areas (AIPE tags) | three-phase-circuits, complex-power, transmission-lines, transformers, per-unit-system, symmetrical-components, load-flow, faults-and-protection, hvdc, electromechanics, synchronous-machines, induction-machines, dc-and-pm-machines, motor-drives |
| Relevant AIPE modules | `ps.three-phase` (core), `ps.components` (core), `ps.transformers` (partial), `ps.per-unit` (partial), `ps.faults` (core), `ps.machines` (core), `ps.power-flow` (partial), `f.magnetism` (partial), `ps.protection` (introductory), `pe.inverters` (introductory), `pe.rectifiers` (introductory), `pe.topologies` (introductory), `pe.buck` (introductory), `pe.boost` (introductory), `pe.applications` (introductory), `ps.dc-grids` (introductory) |
| Lessons citing this course | `three-phase-fundamentals` |
| Access limitations | No lecture-notes page and no lecture videos exist for this course: the learning-resource types are Problem Sets, Problem Set Solutions, Exams, Exam Solutions and Open Textbooks, and probes of pages/lecture-notes/, pages…; Chapter 7 of the course notes (Power electric motor drives) is stated on the readings page as not available on MIT OpenCourseWare; the readings page also points out that the notes have no power-electronics chapter.; PDF content (course-note chapters, the combined open textbook, problem sets, solutions, quizzes) and the assn07.m program file were not opened or downloaded, per the metadata-only rule; depth within each chapter or assi…; (+3 more in the JSON source) |
| Verification | verified on 2026-10-20 (HTTP 200; syllabus HTTP 200) |

Official resource pages (summaries in `references/mit-ocw-coverage.json`):

- [Course-home](https://ocw.mit.edu/courses/6-061-introduction-to-electric-power-systems-spring-2011/)
- [Syllabus](https://ocw.mit.edu/courses/6-061-introduction-to-electric-power-systems-spring-2011/pages/syllabus/)
- [Calendar](https://ocw.mit.edu/courses/6-061-introduction-to-electric-power-systems-spring-2011/pages/calendar/)
- [Course-notes-listing (open textbook chapters)](https://ocw.mit.edu/courses/6-061-introduction-to-electric-power-systems-spring-2011/pages/readings/)
- [Open-textbook (single pdf resource page)](https://ocw.mit.edu/courses/6-061-introduction-to-electric-power-systems-spring-2011/resources/6_061_s11_textbook_pdf/)
- [Problem-sets](https://ocw.mit.edu/courses/6-061-introduction-to-electric-power-systems-spring-2011/pages/assignments/)
- [Problem-set supporting file (html resource page)](https://ocw.mit.edu/courses/6-061-introduction-to-electric-power-systems-spring-2011/resources/assn07/)
- [Exams](https://ocw.mit.edu/courses/6-061-introduction-to-electric-power-systems-spring-2011/pages/quizzes/)
- [Course-download](https://ocw.mit.edu/courses/6-061-introduction-to-electric-power-systems-spring-2011/download)

Scope (AIPE summary in its own words):

MIT 6.061 (with a graduate variant 6.690) is an advanced-undergraduate (OCW level: Undergraduate) introduction to electric power systems and electromechanical energy conversion, taught by Prof. James L. Kirtley Jr. in Spring 2011 with two 1.5-hour lectures per week. The 23-lecture calendar starts with a review of network theory, first-order transients (using buck and boost converters as examples) and sinusoidal steady state, then covers transmission lines, polyphase circuits, transformers and per-unit, symmetrical components, faults, protection, phase control and HVDC, and load flow. The second half turns to electromechanics (forces, virtual work) and synchronous, induction, DC and permanent-magnet machines including drive control, and closes with switching power-electronic circuits and inverters. Published materials are a 12-chapter set of course notes labelled '2007 Course Notes' (11…

### MIT 6.685 — Electric Machines (Fall 2013)

| Field | Value |
| --- | --- |
| Official URL | <https://ocw.mit.edu/courses/6-685-electric-machines-fall-2013/> |
| Course number(s) | 6.685 |
| Teaching term | Fall 2013 |
| Level (MIT) | Graduate |
| Instructor(s) as listed | Prof. James L. Kirtley Jr. |
| AIPE priority | supplementary |
| AIPE reference area | Electromechanical energy conversion |
| Available public resources | Lecture Notes, Instructor Insights, Problem Sets, Problem Set Solutions, Exams, Exam Solutions |
| Main knowledge areas (AIPE tags) | electric-machines, electromechanical-energy-conversion, synchronous-machines, induction-machines, dc-machines, permanent-magnet-machines, park-transform, magnetic-circuits, machine-design-and-sizing, motor-drives, doubly-fed-induction-generator, per-unit-system |
| Relevant AIPE modules | `ps.machines` (core), `ps.stability` (introductory), `ps.per-unit` (partial), `ps.transformers` (introductory), `f.magnetism` (partial), `f.electromagnetism` (partial), `re.wind` (introductory), `pe.applications` (introductory) |
| Lessons citing this course | — |
| Access limitations | No lecture videos or readings are published: video_galleries/lecture-videos/ and pages/readings/ each 301-redirect to a resources/<name>/index.html URL that then redirects to itself (an infinite 301 loop; curl reached n…; pages/lecture-notes/ 301-redirects to resources/lecture-notes/index.html (HTTP 200), an auto-generated listing of the same 12 chapters sorted alphabetically (1, 10, 11, 12, 2, ...), so chapter order was taken from the c…; All course notes, problem sets, solutions and quizzes are PDFs that were not opened, so lecture and chapter titles are the only content evidence; the depth of any single lecture (e.g. what 'Induction Motor Drives and Co…; (+4 more in the JSON source) |
| Verification | verified on 2026-10-20 (HTTP 200; syllabus HTTP 200) |

Official resource pages (summaries in `references/mit-ocw-coverage.json`):

- [Course-home](https://ocw.mit.edu/courses/6-685-electric-machines-fall-2013/)
- [Syllabus](https://ocw.mit.edu/courses/6-685-electric-machines-fall-2013/pages/syllabus/)
- [Calendar](https://ocw.mit.edu/courses/6-685-electric-machines-fall-2013/pages/calendar/)
- [Lecture-notes](https://ocw.mit.edu/courses/6-685-electric-machines-fall-2013/pages/course-notes/)
- [Lecture-notes-listing](https://ocw.mit.edu/courses/6-685-electric-machines-fall-2013/resources/lecture-notes/index.html)
- [Problem-sets](https://ocw.mit.edu/courses/6-685-electric-machines-fall-2013/pages/assignments/)
- [Exams](https://ocw.mit.edu/courses/6-685-electric-machines-fall-2013/pages/exams/)
- [Instructor-insights](https://ocw.mit.edu/courses/6-685-electric-machines-fall-2013/pages/instructor-insights/)
- [Course-download](https://ocw.mit.edu/courses/6-685-electric-machines-fall-2013/download/)

Scope (AIPE summary in its own words):

A graduate course on electromechanics that uses electric machinery as its running example. It starts from field- and energy-based force calculation and magnetic circuits, then covers windings and air-gap fields and the major machine classes: round-rotor and two-reaction (Park transform) synchronous machines with their dynamics and simulation, induction machines (transformer model, squirrel-cage, drives and control, doubly-fed, single-phase, linear), DC commutator machines, variable-reluctance machines and permanent-magnet brushless DC motors, plus transformers, per-unit normalisation, machine sizing and power density, and design evaluation. The stated approach is deliberately classical and analytical, using numerical methods only when necessary; students are expected to be able to design the main classes of rotating and linear machines and to estimate their dynamic parameters. Research-…

### MIT 6.691 — Seminar in Electric Power Systems (Spring 2006)

| Field | Value |
| --- | --- |
| Official URL | <https://ocw.mit.edu/courses/6-691-seminar-in-electric-power-systems-spring-2006/> |
| Course number(s) | 6.691 |
| Teaching term | Spring 2006 |
| Level (MIT) | Graduate |
| Instructor(s) as listed | Prof. James L. Kirtley Jr. |
| AIPE priority | supplementary |
| AIPE reference area | Grid operation and stability |
| Available public resources | Lecture Notes, Projects with Examples, Problem Sets, Problem Set Solutions |
| Main knowledge areas (AIPE tags) | power-flow, newton-raphson, transmission-line-models, circle-diagrams, synchronous-machine-modelling, per-unit-system, electromechanical-dynamics, small-signal-stability, voltage-regulator-pss, economic-dispatch, optimal-dispatch, symmetrical-components, fault-analysis, protective-relaying |
| Relevant AIPE modules | `ps.power-flow` (core), `ps.stability` (core), `ps.faults` (core), `ps.grid-control` (core), `ps.machines` (partial), `ps.components` (partial), `ps.protection` (partial), `ps.three-phase` (partial), `f.computation` (partial), `ps.per-unit` (introductory), `ps.transformers` (introductory) |
| Lessons citing this course | — |
| Access limitations | pages/calendar/ is not a separate page: it returns 301 to .../resources/calendar/index.html, which redirects back (curl aborted after 50 redirects with exit 47, 0 bytes). The calendar is embedded in the syllabus page an…; There are no lecture videos and no per-lecture notes. The Lecture Notes page lists a single PDF ('Plans and Directions') and refers to the 6.061 notes; the PDF was not opened, so the actual depth of each listed lecture…; The syllabus states that the calendar is a 'straw man' expected to change and that content varies each year, so the delivered Spring 2006 sequence may have differed from the listed one.; (+8 more in the JSON source) |
| Verification | verified on 2026-10-20 (HTTP 200; syllabus HTTP 200) |

Official resource pages (summaries in `references/mit-ocw-coverage.json`):

- [Course home page](https://ocw.mit.edu/courses/6-691-seminar-in-electric-power-systems-spring-2006/)
- [Syllabus with embedded calendar](https://ocw.mit.edu/courses/6-691-seminar-in-electric-power-systems-spring-2006/pages/syllabus/)
- [Lecture notes listing](https://ocw.mit.edu/courses/6-691-seminar-in-electric-power-systems-spring-2006/pages/lecture-notes/)
- [Problem sets and solutions listing](https://ocw.mit.edu/courses/6-691-seminar-in-electric-power-systems-spring-2006/pages/assignments/)
- [Projects with examples](https://ocw.mit.edu/courses/6-691-seminar-in-electric-power-systems-spring-2006/pages/projects/)
- [Tools (matlab scripts)](https://ocw.mit.edu/courses/6-691-seminar-in-electric-power-systems-spring-2006/pages/tools/)
- [Course download page (not fetched)](https://ocw.mit.edu/courses/6-691-seminar-in-electric-power-systems-spring-2006/download)

Scope (AIPE summary in its own words):

MIT 6.691 (Spring 2006, graduate, Prof. James L. Kirtley Jr.) is a seminar on how bulk electric power systems are planned and operated, taught mainly from an engineering viewpoint with some attention to the economics of a restructured industry. Its self-described 'straw man' calendar runs from a review of complex power and polyphase systems through transmission-line two-port models and sending/receiving-end circle diagrams, transformers, Newton-Raphson and decoupled load flow, synchronous-machine modelling and per-unit models, electromechanical dynamics, voltage regulators and power system stabilizers, small-signal behaviour, generation costs and economic/optimal dispatch, symmetrical components, fault modelling and relaying. The home-page course description (the only fetched page that carries the 'core topics' list) additionally names, as core themes, system protection, multimachine dy…

## Renewable Energy

Solar photovoltaics, wind, energy storage, energy conversion, and the grid integration of renewable generation through power electronics and power systems.

Also relevant (primary domain elsewhere): MIT 6.685.

### MIT 2.627 — Fundamentals of Photovoltaics (Fall 2013)

| Field | Value |
| --- | --- |
| Official URL | <https://ocw.mit.edu/courses/2-627-fundamentals-of-photovoltaics-fall-2013/> |
| Course number(s) | 2.626, 2.627 |
| Teaching term | Fall 2013 |
| Level (MIT) | Undergraduate |
| Instructor(s) as listed | Prof. Tonio Buonassisi |
| AIPE priority | core |
| AIPE reference area | Solar photovoltaic technology |
| Available public resources | Lecture Videos, Tutorial Videos, Problem Sets, Lecture Notes, Projects with Examples, Problem Set Solutions |
| Main knowledge areas (AIPE tags) | solar-resource, light-absorption, pn-junction, charge-carrier-transport, solar-cell-iv-characteristic, efficiency-limits, silicon-solar-cells, thin-film-pv, solar-cell-characterization, pv-modules-and-reliability, pv-cost-and-manufacturing, pv-markets-and-policy |
| Relevant AIPE modules | `re.pv` (core), `f.electronics` (partial), `re.conversion` (partial), `re.pv-systems` (introductory), `re.system-design` (partial) |
| Lessons citing this course | `solar-pv-fundamentals` |
| Access limitations | pages/calendar/ and pages/projects/ answer HTTP 301 into a redirect loop (to resources/calendar/index.html and resources/projects/index.html, which 301 again; curl with --max-redirs 8 still ends on a 301, reproduced on…; pages/assignments/ answers HTTP 301 to resources/assignments/index.html, which loads (HTTP 200) but reads 'No Resources Found'; the real assignments page is video_galleries/assignments/.; The pages/lecture-notes/ and pages/readings/ listings are not linked from the course menu (Syllabus, Calendar & Readings, IV Curve Measurement, Lecture Videos & Slides, Tutorial Videos, Assignments, Quizzes, Related Res…; (+5 more in the JSON source) |
| Verification | verified on 2026-10-20 (HTTP 200; syllabus HTTP 200) |

Official resource pages (summaries in `references/mit-ocw-coverage.json`):

- [Course home page](https://ocw.mit.edu/courses/2-627-fundamentals-of-photovoltaics-fall-2013/)
- [Syllabus](https://ocw.mit.edu/courses/2-627-fundamentals-of-photovoltaics-fall-2013/pages/syllabus/)
- [Calendar and readings](https://ocw.mit.edu/courses/2-627-fundamentals-of-photovoltaics-fall-2013/pages/calendar-readings/)
- [Lab page](https://ocw.mit.edu/courses/2-627-fundamentals-of-photovoltaics-fall-2013/pages/calendar-readings/iv-curve-measurement/)
- [Lecture videos and slides gallery](https://ocw.mit.edu/courses/2-627-fundamentals-of-photovoltaics-fall-2013/video_galleries/lecture-videos-slides/)
- [Tutorial videos gallery](https://ocw.mit.edu/courses/2-627-fundamentals-of-photovoltaics-fall-2013/video_galleries/tutorial-videos/)
- [Lecture notes listing](https://ocw.mit.edu/courses/2-627-fundamentals-of-photovoltaics-fall-2013/pages/lecture-notes/)
- [Assignments page (video gallery)](https://ocw.mit.edu/courses/2-627-fundamentals-of-photovoltaics-fall-2013/video_galleries/assignments/)
- [Quizzes](https://ocw.mit.edu/courses/2-627-fundamentals-of-photovoltaics-fall-2013/pages/quizzes/)
- [Readings listing](https://ocw.mit.edu/courses/2-627-fundamentals-of-photovoltaics-fall-2013/pages/readings/)
- [Related resources](https://ocw.mit.edu/courses/2-627-fundamentals-of-photovoltaics-fall-2013/pages/related-resources/)

Scope (AIPE summary in its own words):

MIT 2.627 Fundamentals of Photovoltaics (Fall 2013; the OCW data.json also records the companion number 2.626, which no fetched HTML page shows) is an elective in MIT's undergraduate Energy Studies Minor covering the physics of photovoltaic conversion, how cells are made and evaluated, and the market and policy context in which PV technologies compete. The Fall 2013 calendar has 26 sessions in three units: Unit 1 device fundamentals (solar resource, light management, charge excitation, separation, transport and collection, a 1D device model, materials properties), Unit 2 commercial and emerging technologies (wafer silicon, thin films, efficiency limits, emerging concepts, a Fraunhofer CSE field trip), and Unit 3 cross-cutting themes (efficiency-loss troubleshooting; cost and manufacturability with an industry guest lecture on silicon cell manufacturing costs; modules, systems and reliab…

### MIT 10.626 — Electrochemical Energy Systems (Spring 2014)

| Field | Value |
| --- | --- |
| Official URL | <https://ocw.mit.edu/courses/10-626-electrochemical-energy-systems-spring-2014/> |
| Course number(s) | 10.426, 10.626 |
| Teaching term | Spring 2014 |
| Level (MIT) | Graduate |
| Instructor(s) as listed | Prof. Martin Bazant |
| AIPE priority | supplementary |
| AIPE reference area | Energy storage |
| Available public resources | Problem Sets, Lecture Notes, Instructor Insights, Exams, Exam Solutions |
| Main knowledge areas (AIPE tags) | electrochemical-energy-storage, batteries, lithium-ion-batteries, fuel-cells, supercapacitors, equivalent-circuit-models, impedance-spectroscopy, nernst-equation, butler-volmer-kinetics, electrochemical-transport, porous-electrodes, electrochemical-thermodynamics |
| Relevant AIPE modules | `re.batteries` (core), `re.storage` (partial), `re.conversion` (partial) |
| Lessons citing this course | — |
| Access limitations | No lecture videos or audio: the learning resource types listed are Lecture Notes, Problem Sets, Exams, Exam Solutions and Instructor Insights only.; Problem-set solutions are stated to be unavailable on the assignments page; final-exam solutions are stated to be not available on the exams page (only the midterm has solutions).; The lecture-notes page provides Spring 2014 notes for 15 of the 38 sessions (14 PDFs in 14 rows: sessions 2, 3, 11, 12, 13, 14, 19, 20-21 (one shared PDF), 22, 23, 24, 28, 29 and 33); for 21 sessions (20 rows) no 2014 n…; (+4 more in the JSON source) |
| Verification | verified on 2026-10-20 (HTTP 200; syllabus HTTP 200) |

Official resource pages (summaries in `references/mit-ocw-coverage.json`):

- [Course-home](https://ocw.mit.edu/courses/10-626-electrochemical-energy-systems-spring-2014/)
- [Syllabus](https://ocw.mit.edu/courses/10-626-electrochemical-energy-systems-spring-2014/pages/syllabus/)
- [Calendar](https://ocw.mit.edu/courses/10-626-electrochemical-energy-systems-spring-2014/pages/calendar/)
- [Lecture-notes-listing](https://ocw.mit.edu/courses/10-626-electrochemical-energy-systems-spring-2014/pages/lecture-notes/)
- [Problem-sets](https://ocw.mit.edu/courses/10-626-electrochemical-energy-systems-spring-2014/pages/assignments/)
- [Exams](https://ocw.mit.edu/courses/10-626-electrochemical-energy-systems-spring-2014/pages/exams/)
- [Study-materials](https://ocw.mit.edu/courses/10-626-electrochemical-energy-systems-spring-2014/pages/study-materials/)
- [Instructor-insights](https://ocw.mit.edu/courses/10-626-electrochemical-energy-systems-spring-2014/pages/instructor-insights/)
- [Download-bundle](https://ocw.mit.edu/courses/10-626-electrochemical-energy-systems-spring-2014/download)

Scope (AIPE summary in its own words):

MIT 10.626 Electrochemical Energy Systems, Spring 2014, Prof. Martin Bazant, Department of Chemical Engineering, graduate level. The Instructor Insights page states that the class contains both graduate and undergraduate students and that students taking the graduate version complete additional assignments; the course number 10.426 appears only in the course's data.json as recorded in references/mit-ocw-verification.json (observed.extra_course_numbers), not on any of the eight fetched HTML pages. The course teaches the physics and mathematical modelling of electrochemical energy conversion and storage in five parts: I Introduction (galvanic cells, conversion, storage), II Circuit Models (equivalent-circuit dynamics and impedance), III Thermodynamics (statistical thermodynamics and solution models, Nernst equation and open-circuit voltage, Pourbaix diagrams, metal-acid and Li-ion cells,…

### MIT 15.031J — Energy Decisions, Markets, and Policies (Spring 2012)

| Field | Value |
| --- | --- |
| Official URL | <https://ocw.mit.edu/courses/15-031j-energy-decisions-markets-and-policies-spring-2012/> |
| Course number(s) | 11.161J, 14.43J, 15.031J, 21A.341J |
| Teaching term | Spring 2012 |
| Level (MIT) | Undergraduate |
| Instructor(s) as listed | Prof. Richard Schmalensee |
| AIPE priority | supplementary |
| AIPE reference area | Energy systems and economics |
| Available public resources | Lecture Videos, Lecture Notes, Written Assignments, Instructor Insights |
| Main knowledge areas (AIPE tags) | energy-economics, energy-policy, electricity-markets-and-regulation, energy-demand-and-efficiency, non-renewable-resources, climate-policy, energy-business-decisions, path-dependence, electric-power-system-overview, comparative-energy-systems |
| Relevant AIPE modules | `re.conversion` (introductory), `re.system-design` (partial), `ps.grid-control` (introductory) |
| Lessons citing this course | — |
| Access limitations | All eight content pages used for this mapping (home, syllabus, calendar, lecture notes, video gallery, assignments, readings, recitations) returned HTTP 200 on 2026-10-20 and were re-fetched for this revision; the instr…; Lecture 7 (Climate Agreement Negotiations I) has no video: the video gallery page states it was an in-class activity and is not included (21 of 24 lecture sessions have videos; L23-L24 are student presentations).; The lecture-22 guest talk on micron-gap thermal photovoltaics is marked 'no slides' on the lecture notes page, and the lecture-22 video is listed only under the title 'Economic Development & Green Growth'.; (+4 more in the JSON source) |
| Verification | verified on 2026-10-20 (HTTP 200; syllabus HTTP 200) |

Official resource pages (summaries in `references/mit-ocw-coverage.json`):

- [Course home page](https://ocw.mit.edu/courses/15-031j-energy-decisions-markets-and-policies-spring-2012/)
- [Syllabus](https://ocw.mit.edu/courses/15-031j-energy-decisions-markets-and-policies-spring-2012/pages/syllabus/)
- [Calendar](https://ocw.mit.edu/courses/15-031j-energy-decisions-markets-and-policies-spring-2012/pages/calendar/)
- [Lecture notes (listed as 'lecture slides')](https://ocw.mit.edu/courses/15-031j-energy-decisions-markets-and-policies-spring-2012/pages/lecture-notes/)
- [Lecture videos](https://ocw.mit.edu/courses/15-031j-energy-decisions-markets-and-policies-spring-2012/video_galleries/video-lectures/)
- [Assignments (written)](https://ocw.mit.edu/courses/15-031j-energy-decisions-markets-and-policies-spring-2012/pages/assignments/)
- [Readings](https://ocw.mit.edu/courses/15-031j-energy-decisions-markets-and-policies-spring-2012/pages/readings/)
- [Recitations](https://ocw.mit.edu/courses/15-031j-energy-decisions-markets-and-policies-spring-2012/pages/recitations/)
- [Instructor insights](https://ocw.mit.edu/courses/15-031j-energy-decisions-markets-and-policies-spring-2012/pages/instructor-insights/)

Scope (AIPE summary in its own words):

An undergraduate social-science survey course (Sloan School of Management, jointly offered with Economics, Anthropology, and Urban Studies and Planning; the OCW HTML pages show only the number 15.031J, while the project's verification record lists the additional numbers 14.43J, 21A.341J and 11.161J taken from the course data.json; a core subject of MIT's Energy Studies Minor) on how energy choices are made at every level from the individual household up to firms, movements and governments, drawing on economics, management, political science, sociology and anthropology. Six units run from an overview of the U.S. and comparative energy systems, through the climate problem (including a simulation-based negotiation role play), household and business decision-making (energy demand economics, financial and normative frameworks, cases on combined heat and power and biodiesel, strategy and busi…

### MIT 2.60J — Fundamentals of Advanced Energy Conversion (Spring 2020)

| Field | Value |
| --- | --- |
| Official URL | <https://ocw.mit.edu/courses/2-60j-fundamentals-of-advanced-energy-conversion-spring-2020/> |
| Course number(s) | 10.390J, 10.392J, 2.60J, 2.62J, 22.40J |
| Teaching term | Spring 2020 |
| Level (MIT) | Undergraduate |
| Instructor(s) as listed | Prof. Ahmed F. Ghoniem |
| AIPE priority | supplementary |
| AIPE reference area | Energy conversion |
| Available public resources | Lecture Notes, Projects with Examples, Problem Sets, Problem Set Solutions |
| Main knowledge areas (AIPE tags) | thermodynamics, energy-conversion-efficiency, chemical-thermodynamics, gas-separation, gas-liquefaction-and-storage, electrochemistry, fuel-cells, hydrogen-electrolysis, batteries, energy-storage, solar-photovoltaics, solar-thermal, geothermal-energy, wind-energy, biomass-energy, co2-capture |
| Relevant AIPE modules | `re.conversion` (core), `re.storage` (partial), `re.batteries` (partial), `re.pv` (introductory), `re.wind` (introductory), `re.system-design` (introductory) |
| Lessons citing this course | — |
| Access limitations | All seven HTML pages fetched returned HTTP 200 on 2026-10-20, and again when re-fetched during finalisation the same day; no page failed to load.; No lecture videos, readings page or recitations exist for this course on OCW (learning resource types are Lecture Notes, Problem Sets, Problem Set Solutions, Projects with Examples); the Projects page links no student e…; Lectures 13 and 14 were cancelled and have no notes, so 23 lecture-note sessions plus one presentation session (26) were held; one of the six planned homework assignments was cancelled (5 posted, each with solutions); t…; (+5 more in the JSON source) |
| Verification | verified on 2026-10-20 (HTTP 200; syllabus HTTP 200) |

Official resource pages (summaries in `references/mit-ocw-coverage.json`):

- [Course home page](https://ocw.mit.edu/courses/2-60j-fundamentals-of-advanced-energy-conversion-spring-2020/)
- [Syllabus](https://ocw.mit.edu/courses/2-60j-fundamentals-of-advanced-energy-conversion-spring-2020/pages/syllabus/)
- [Calendar](https://ocw.mit.edu/courses/2-60j-fundamentals-of-advanced-energy-conversion-spring-2020/pages/calendar/)
- [Lecture notes listing](https://ocw.mit.edu/courses/2-60j-fundamentals-of-advanced-energy-conversion-spring-2020/pages/lecture-notes/)
- [Problem sets](https://ocw.mit.edu/courses/2-60j-fundamentals-of-advanced-energy-conversion-spring-2020/pages/assignments/)
- [Projects](https://ocw.mit.edu/courses/2-60j-fundamentals-of-advanced-energy-conversion-spring-2020/pages/projects/)
- [Tools](https://ocw.mit.edu/courses/2-60j-fundamentals-of-advanced-energy-conversion-spring-2020/pages/tools/)
- [Download](https://ocw.mit.edu/courses/2-60j-fundamentals-of-advanced-energy-conversion-spring-2020/download)

Scope (AIPE summary in its own words):

MIT 2.60J Fundamentals of Advanced Energy Conversion (Spring 2020; the OCW pages display only the number 2.60J, while the catalogue's verified OCW metadata lists the cross-listings 2.62J, 10.390J, 10.392J and 22.40J; instructor Prof. Ahmed F. Ghoniem; listed level Undergraduate, with the syllabus adding that a graduate version runs on identical content with a heavier assignment load) uses thermodynamics, chemical and electrochemical thermodynamics and transport to examine how energy is converted and stored, judging each process mainly by its efficiency, its delivered performance and its environmental footprint. The 26-session schedule moves from thermodynamic tools for conversion efficiency, gas mixtures, liquefaction and chemical thermodynamics into electrochemistry (electrochemical thermodynamics, fuel cells, electrolysis, batteries), then surveys conversion technologies (solar photov…

### MIT 22.081J — Introduction to Sustainable Energy (Fall 2010)

| Field | Value |
| --- | --- |
| Official URL | <https://ocw.mit.edu/courses/22-081j-introduction-to-sustainable-energy-fall-2010/> |
| Course number(s) | 1.818J, 10.291J, 10.391J, 11.371J, 2.650J, 2.65J, 22.081J, 22.811J, ESD.166J |
| Teaching term | Fall 2010 |
| Level (MIT) | Undergraduate, Graduate |
| Instructor(s) as listed | Prof. Michael Golay, Randall Field, Prof. William Green, Jr., Dr. John C. Wright |
| AIPE priority | supplementary |
| AIPE reference area | Sustainable energy systems |
| Available public resources | Lecture Notes, Written Assignments, Problem Sets |
| Main knowledge areas (AIPE tags) | sustainable-energy, energy-conversion, energy-resources, energy-storage, wind-energy, solar-energy, electric-power-sector, energy-economics, systems-analysis, climate-policy, nuclear-energy, fossil-fuels |
| Relevant AIPE modules | `re.conversion` (core), `re.system-design` (partial), `re.storage` (partial), `re.wind` (introductory), `re.batteries` (introductory), `re.pv` (introductory), `ps.components` (introductory), `ps.grid-control` (introductory), `f.quantities` (introductory) |
| Lessons citing this course | — |
| Access limitations | No lecture videos exist for this course; the only resource types are lecture slides (PDF), problem sets and written assignments, so coverage judgements rest on session titles and the sub-topic bullets on the listing pag…; Five session parts have no slides posted (marked 'none' on the lectures page): 12a Cape Wind, 14a electricity generation options, 16a carbon management, 16b geothermal, and 17 solar photovoltaics and thermal energy; ses…; Per the evidence rules no PDFs were opened; the content of 'Toolbox 6: Electrical systems dynamics' (8a, no bullets listed) and other sessions is known from titles/bullets only.; (+4 more in the JSON source) |
| Verification | verified on 2026-10-20 (HTTP 200; syllabus HTTP 200) |

Official resource pages (summaries in `references/mit-ocw-coverage.json`):

- [Course home page](https://ocw.mit.edu/courses/22-081j-introduction-to-sustainable-energy-fall-2010/)
- [Syllabus](https://ocw.mit.edu/courses/22-081j-introduction-to-sustainable-energy-fall-2010/pages/syllabus/)
- [Calendar](https://ocw.mit.edu/courses/22-081j-introduction-to-sustainable-energy-fall-2010/pages/calendar/)
- [Lecture notes listing](https://ocw.mit.edu/courses/22-081j-introduction-to-sustainable-energy-fall-2010/pages/lectures-and-readings/)
- [Problem sets and exams listing](https://ocw.mit.edu/courses/22-081j-introduction-to-sustainable-energy-fall-2010/pages/assignments-and-exams/)
- [Related resources](https://ocw.mit.edu/courses/22-081j-introduction-to-sustainable-energy-fall-2010/pages/related-resources/)
- [Course download](https://ocw.mit.edu/courses/22-081j-introduction-to-sustainable-energy-fall-2010/download)

Scope (AIPE summary in its own words):

22.081J Introduction to Sustainable Energy (Fall 2010, undergraduate and graduate, listed under six departments: Nuclear Science and Engineering, Mechanical Engineering, Chemical Engineering, Civil and Environmental Engineering, Urban Studies and Planning, Engineering Systems Division) is a survey course that assesses present and future energy systems from resources through extraction, conversion and end use, judged against engineering, economic, political, social and environmental goals. Part I (sessions 1a-9b) builds a quantitative 'toolbox' (energy units and flows, conversion and efficiency, resource depletion, storage and transmission, systems analysis, electric power sector, electrical system dynamics, economic feasibility, thermodynamics, carbon policy); Part II (10-19b) surveys specific technologies (nuclear, fossil, wind, policy, transport, fusion, carbon management, geothermal,…

### MIT 8.21 — The Physics of Energy (Fall 2009)

| Field | Value |
| --- | --- |
| Official URL | <https://ocw.mit.edu/courses/8-21-the-physics-of-energy-fall-2009/> |
| Course number(s) | 8.21 |
| Teaching term | Fall 2009 |
| Level (MIT) | Undergraduate |
| Instructor(s) as listed | Prof. Robert Jaffe, Prof. Washington Taylor |
| AIPE priority | supplementary |
| AIPE reference area | Physical foundations of energy |
| Available public resources | Lecture Notes |
| Main knowledge areas (AIPE tags) | energy-conversion-fundamentals, energy-units-and-scales, thermodynamics-and-heat-engines, power-plant-cycles, electromagnetic-energy-and-transmission, solar-radiation-and-photovoltaics, wind-resource-and-aerodynamics, nuclear-energy-physics, energy-storage-physics, renewable-resource-limits, climate-physics, energy-conservation-and-end-use |
| Relevant AIPE modules | `re.conversion` (core), `re.pv` (partial), `re.wind` (partial), `re.storage` (introductory), `f.quantities` (introductory), `f.electromagnetism` (introductory) |
| Lessons citing this course | — |
| Access limitations | The site navigation lists no Calendar page. The probed URL pages/calendar/ returned HTTP 301 to resources/calendar/index.html on 2026-10-20, and that URL 301-redirects to itself (curl aborts after 50 redirects, exit cod…; OCW lists only 'Lecture Notes' as a learning resource type. No problem-set, exam, video, readings or recitation pages are published for this course, although the syllabus says weekly problem sets, two in-class exams and…; Lecture-slide links exist only for sessions 1-12 (Introduction and Part I). Sessions 13-38 (Parts II and III) are listed as titles only, so coverage judgments for nuclear, solar, wind, geothermal, hydro, climate, storag…; (+4 more in the JSON source) |
| Verification | verified on 2026-10-20 (HTTP 200; syllabus HTTP 200) |

Official resource pages (summaries in `references/mit-ocw-coverage.json`):

- [Course home page](https://ocw.mit.edu/courses/8-21-the-physics-of-energy-fall-2009/)
- [Syllabus](https://ocw.mit.edu/courses/8-21-the-physics-of-energy-fall-2009/pages/syllabus/)
- [Lecture notes listing](https://ocw.mit.edu/courses/8-21-the-physics-of-energy-fall-2009/pages/lecture-notes/)
- [Related resources listing](https://ocw.mit.edu/courses/8-21-the-physics-of-energy-fall-2009/pages/related-resources/)
- [Download page (not fetched)](https://ocw.mit.edu/courses/8-21-the-physics-of-energy-fall-2009/download)

Scope (AIPE summary in its own words):

MIT 8.21 The Physics of Energy (Physics Department, Fall 2009, undergraduate; instructors listed as Prof. Robert Jaffe and Prof. Washington Taylor) is a quantitative physics course on energy for students who already have introductory physics, calculus and chemistry: it asks where energy comes from, how it is extracted, moved, stored, lost and finally used, and which physical laws limit each step. Part I (Energy and its Uses) covers energy units and scales, mechanical, thermal and electromagnetic energy, an introduction to quantum energy levels, chemical energy and CO2 flows, entropy and temperature, heat engines, phase-change conversion with refrigeration and heat pumps, internal combustion engines, and steam and gas power cycles. Part II (Sources of Energy) covers fundamental forces, quantum mechanics for nuclear physics, nuclear forces and binding energy, fusion, fission and fission-r…

### MIT EC.S07 — Photovoltaic Solar Energy Systems (Fall 2004)

| Field | Value |
| --- | --- |
| Official URL | <https://ocw.mit.edu/courses/ec-s07-photovoltaic-solar-energy-systems-fall-2004/> |
| Course number(s) | EC.S07 |
| Teaching term | Fall 2004 |
| Level (MIT) | Undergraduate |
| Instructor(s) as listed | Prof. Louis Bucciarelli |
| AIPE priority | supplementary |
| AIPE reference area | Solar system engineering |
| Available public resources | Lecture Notes, Written Assignments, Activity Assignments |
| Main knowledge areas (AIPE tags) | photovoltaics, solar-resource, solar-geometry, clearness-index, pv-module-iv-characteristics, array-orientation-tracking, stand-alone-pv, pv-system-sizing, loss-of-load-probability, battery-storage, grid-connected-pv, pv-economics-npv |
| Relevant AIPE modules | `re.pv` (partial), `re.pv-systems` (core), `re.system-design` (core), `re.conversion` (partial), `re.storage` (partial), `re.batteries` (introductory), `re.mppt` (introductory), `re.integration` (introductory), `re.energy-management` (introductory), `f.computation` (introductory) |
| Lessons citing this course | `solar-pv-fundamentals` |
| Access limitations | No lecture videos: the learning resource types are Lecture Notes, Written Assignments and Activity Assignments only.; The lecture notes page states that only some of the class lecture notes are provided; 4 PDFs exist for a 14-session course, so most sessions have no notes on OCW.; Readings were handed out in class and are not on OCW; the syllabus names no textbook.; (+6 more in the JSON source) |
| Verification | verified on 2026-10-20 (HTTP 200; syllabus HTTP 200) |

Official resource pages (summaries in `references/mit-ocw-coverage.json`):

- [Course home page](https://ocw.mit.edu/courses/ec-s07-photovoltaic-solar-energy-systems-fall-2004/)
- [Syllabus](https://ocw.mit.edu/courses/ec-s07-photovoltaic-solar-energy-systems-fall-2004/pages/syllabus/)
- [Calendar](https://ocw.mit.edu/courses/ec-s07-photovoltaic-solar-energy-systems-fall-2004/pages/calendar/)
- [Lecture notes listing](https://ocw.mit.edu/courses/ec-s07-photovoltaic-solar-energy-systems-fall-2004/pages/lecture-notes/)
- [Assignments listing](https://ocw.mit.edu/courses/ec-s07-photovoltaic-solar-energy-systems-fall-2004/pages/assignments/)
- [Study materials listing](https://ocw.mit.edu/courses/ec-s07-photovoltaic-solar-energy-systems-fall-2004/pages/study-materials/)
- [Tools](https://ocw.mit.edu/courses/ec-s07-photovoltaic-solar-energy-systems-fall-2004/pages/tools/)
- [Related resources](https://ocw.mit.edu/courses/ec-s07-photovoltaic-solar-energy-systems-fall-2004/pages/related-resources/)
- [Course download](https://ocw.mit.edu/courses/ec-s07-photovoltaic-solar-energy-systems-fall-2004/download)

Scope (AIPE summary in its own words):

EC.S07 (Edgerton Center, Fall 2004, undergraduate, Prof. Louis Bucciarelli) is a one-session-per-week, two-hour class (the syllabus labels the meetings 'Lectures') on the behaviour and first-order conceptual design of photovoltaic systems, with the emphasis on stand-alone (off-grid) PV-plus-battery systems for any location in the US. The 14-session calendar moves from the solar resource (sun geometry, clearness index, US insolation databases and TMY data) through module I-V behaviour and array networking to stand-alone system elements, three sessions of stand-alone sizing (first-order estimation of average daily performance, then loss-of-load probability with a Markov process model and the effect of day-to-day correlation), evaluation of PV station data, two sessions on grid-connected systems (power conditioning, utility constraints, architectural/structural considerations) and cost/ben…
