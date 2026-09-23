# The Unofficial Guide

<!-- Replace this line with your name and which corpus you picked. -->

> **This file is your submission.** Fill it in as you go — most sections get
> written during the milestone that produces them, not at the end.
>
> How the starter works, and every command you'll need, is in `RUNNING.md`.
> Leave that file alone.
>
> **Paste everything as text.** No screenshots, no video. A typed table gets
> full credit; a picture of the same table gets none.
>
> Delete these instruction blocks as you replace them. The `<!-- -->` comments
> are notes to you and don't show up when the page renders — you can leave them
> or remove them.

---

# Unit 1

## What This Does
This is a RAG system that answers questions about student life at a university, using campus_life, a set of 88 short student-written posts about dining, housing, admin rules, courses. It retrieves the most relevant post for a question and answers using only the content, citing the source file. If a question isn't covered by the documents, a relevance gate catches it and the system says so rather than guessing. Example questions it can answer include things like "What is the expected workload outside of class for a week in CS 210?" and "What are the wait times like at kestrel commons during Lunch?"
<!-- Three or four sentences. Which corpus you picked, and the kinds of
     questions your system answers. Write it for someone who has never seen
     this repo.

     Milestone 5. -->

## Chunking Strategy

**Chunk size:** 600
**Overlap:** 60

Document lengths across all 88 campus_life files run from 178 to 563
characters, median 315 - every single post fits under 600, so that's set
just above the longest real document rather than a round generic number
like 800. The intent is that whole posts stay whole.

I checked whether paragraph structure argued for splitting anyway. Most
posts have 3-5 blank-line-separated paragraphs, but the first is almost
always a bare one-line title ("On the add/drop deadline", "Re: Halden
Hall"), and the rest is 1-2 short body paragraphs building one point (e.g.
the CS 210 workload post: "8-10 hrs/week" then "front-loaded"). Splitting
on blank lines would strand a title on its own and separate a claim from
its immediate qualifier - worse than keeping the post as one chunk.

The one real exception is the dining-hall `_followup` files, which do stack
two independent facts (wait time + closing time, in
`dining_halden_hall_followup.txt`). I'm accepting that as the legitimate
miss already called out in criteria.md #4, rather than building a splitting
rule around ~7 files that would break the other 80+ posts that are
genuinely one thought.

Overlap of 60 (~10% of chunk size) exists only as a safety net for the rare
case a document exceeds 600 characters - it should almost never fire on
this corpus, but it avoids a hard cutoff with no shared context if a post
grows past the cap later.


## Sample Chunks

<!-- Five chunks, pasted as text. Label each one and name the file it came from
     AND the function that produced it — the grader checks your code against
     what you claim here.

     `python app.py chunks -n 5` prints all three for you. Copy them straight
     across.

     Milestone 3. -->

**Chunk 1** - source: `admin_add_drop_deadline.txt#0` - produced by: `chunker.py::split_documents`

```
On the add/drop deadline

You can add a course through the end of the second week. Dropping is a longer window - through the end of week six - but a drop after week two shows as a W on your transcript. Nothing anywhere on the registrar's site says this plainly, and students find out from each other.
```

**Chunk 2** - source: `course_biol_160.txt#0` - produced by: `chunker.py::split_documents`

```
BIOL 160 Cell Biology

I lived here my sophomore year. Format is lecture three times a week with a weekly lab. Assessment: four unit tests and a cumulative final. Not curved.

Expect 9 to 11 hours a week, the heaviest first-year course by reputation.

The one piece of advice: the unit tests come fast, roughly every three weeks; falling behind once is very hard to recover from.
```

**Chunk 3** - source: `course_hist_118_workload.txt#0` - produced by: `chunker.py::split_documents`

```
Workload for HIST 118 Modern World History

People keep asking so: a lot of reading, about 120 pages a week, but no problem sets. That's real time, not optimistic time.

It's front-loaded - the first month is heavier than the rest, partly because you're learning the format.
```

**Chunk 4** - source: `dining_pellew_dining_hall_followup.txt#0` - produced by: `chunker.py::split_documents`

```
Re: Pellew Dining Hall

Adding to what people have said about Pellew Dining Hall. The wait figure of 12 to 18 minutes at peak matches what I've seen. If you're trying to eat between classes, go before 11:45 and it's a different building entirely.

Also worth saying: the furthest hall from anywhere, next to the athletics centre. Nobody tells you this at orientation.
```

**Chunk 5** - source: `housing_innisfree_hall.txt#0` - produced by: `chunker.py::split_documents`

```
Innisfree Hall - what it's actually like

Transferred in last year, so take this with a grain of salt. Built 1991, renovated 2022. Rooms are doubles arranged as pairs sharing one bathroom between two rooms.

The good: the shared-bathroom-between-two-rooms arrangement is the best compromise on campus.

The bad: no air conditioning, which matters for the first three weeks of September.

Laundry costs $1.75 wash, $1.75 dry, app-based. On noise: moderate; the building is L-shaped and the short wing is much quieter.
```

## Sample Answer

**Question:** How much does laundry cost at Innisfree Hall?

**Answer:**

```
Laundry at Innisfree Hall costs $1.75 for a wash and $1.75 for a dry.

Sources: `housing_innisfree_hall_laundry.txt` and `housing_innisfree_hall.txt`
```

(best distance 0.201, cutoff 0.6). Retrieval also pulled in
`housing_aldridge_hall.txt`, `housing_aldridge_hall_laundry.txt`, and
`housing_calder_annexe.txt`, near-identical sibling docs with different
prices ($1.75/$1.50 and $2.00/$1.75), and the model still attributed the
right numbers to the right building.

**My relevance cutoff:**

I set `THRESHOLD = 0.6` in `config.py` (the starter default). My five in-corpus
questions had best distances of 0.175-0.372, and the five `OUT_OF_SCOPE`
questions had best distances of 0.825-0.934, a clean gap from about 0.37 to
0.82 with no overlap between the two groups. 0.6 sits in the middle of that
gap rather than hugging either edge, which gives the most margin against a
future question landing close to either group's boundary.

| Question | In corpus? | Best distance |
|---|---|---|
| What are the wait times like at kestrel commons during Lunch? | yes | 0.177 |
| What is the last week of the semester that you can withdraw from a class? | yes | 0.372 |
| What is the expected workload outside of class for a week in CS 210? | yes | 0.204 |
| What is a student's printing budget per semester? | yes | 0.310 |
| How are juniors and seniors ordered in the housing lottery, as opposed to rising sophomores? | yes | 0.175 |
| What is the capital of Mongolia? | no | 0.825 |
| How do I change the oil in a diesel engine? | no | 0.934 |
| Who won the 1994 World Cup? | no | 0.886 |
| What is the recommended dosage of ibuprofen for a headache? | no | 0.844 |
| How do I write a for loop in Rust? | no | 0.896 |


## How I Used AI

<!-- Two specific moments. For each: what you asked for, what came back, and
     what you changed about it.

     "I asked Claude to write the chunking function from my notes. It ignored
     the overlap, so I added that myself" is the level of detail we're after.
     "I used AI to help me code" is not.

     Milestone 5. -->

**1.**
I asked Claude "Could someone answer a question using only this chunk without reading what came before or after?" for each of the 5 sample chunks. The check found 2 of 5 actually bundle several unrelated facts about one entity into a single chunk rather than holding one clean topic. Instead of writing a splitting rule to fix these certain files at the risk of breaking the others, I decided to keep them as the honest edge cases which I anticipated in criteria #4. 

**2.**
I asked Claude to verify how the starter's fixed 800-char/120-overlap chunker behaved on other corpora, including city_guides and advice_threads. It came back showing city_guides produces 51 chunks cut mid-section, pinned at the 800 char limit, and advice_threads produces a stray 2-character trailing fragment when a document doesn't divide evenly into the window. This confirmed the 'too small/too big' failure modes existed elsewhere, but also confirmed my own corpus didn't have this issue. Campus_life's actual issue was different, whether a post holding two thoughts should be split at all, which is what drove my 600/60 chunk size decision instead. It's also what shaped how I wrote my 4th criterion. 

## Stretch: Metadata Filtering

**Doing this one.** Retrieval will be narrowed by `category`, a metadata
field derived from the part of each filename before its first underscore
(`housing_calder_annexe.txt` → `"housing"`). It'll be stored on every chunk
at index time in `store.py::build_index` and applied as a Chroma `where`
clause in `store.py::search`, with `--category` exposed on
`python app.py retrieve`.

---

# Unit 2

<!-- These sections get ADDED to what's already above. Don't delete or rewrite
     unit 1 — the point is that someone can see what you said before you knew
     how it went. -->

## Run Log — Before

<!-- Your five criteria, three runs each. `python run_eval.py --label before`
     runs the questions, puts the OUT_OF_SCOPE ones through the gate, and
     writes it all into results/ for you. Targets come from criteria.md; the
     verdict column is your call.

     Criterion 3 is measured in one deterministic pass rather than three, so
     the same number goes in all three run columns. That's correct, not lazy.

     Milestone 1. -->

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Retrieved chunk contains the answer | 4 of 5 |  |  |  |  |
| 2. Every answer names a source | 5 of 5 |  |  |  |  |
| 3. Gate stops out-of-corpus questions | 4 of 5 |  |  |  |  |
| 4. | | | | | |
| 5. | | | | | |

<!-- Underneath, paste the REAL output for each criterion from one of your
     runs — the actual text your system produced, not a description of it.
     Name the file and function that produced it. -->

## Verdicts

<!-- MET or MISSED for each of the five, against the target you wrote last
     unit — not a new one. Plus a sentence on how you decided. That sentence
     matters most where it was close.

     If your target said 4 of 5 and your runs came out 4, 3, 4, that's a MISS.
     The target has to hold, not show up occasionally.

     Milestone 2. -->

| # | Criterion | Verdict | How I decided |
|---|---|---|---|
| 1 |  |  |  |
| 2 |  |  |  |
| 3 |  |  |  |
| 4 |  |  |  |
| 5 |  |  |  |

## Diagnoses

<!-- For each miss: which stage caused it, and how. The stage alone isn't
     enough — you need the mechanism.

     Not a diagnosis: "Question 3 didn't work."
     A diagnosis:     "Question 3 asks about laundry costs. The answer is in
                       one sentence that got split across two chunks, so
                       neither chunk on its own contains it."

     The five stages: loading → chunking → embedding → retrieval → generation.

     Look for a pattern. If three misses all ask about numbers, that's one
     problem, not three.

     Missed nothing? Say so, then say honestly whether your targets were set
     low, and which one you'd tighten and to what.

     Milestone 3. -->

## The Improvement

**What I changed:**

**Why I picked it:**

<!-- Connect it to a specific diagnosis above in one sentence. If you can't,
     you picked a fix because it sounded impressive. -->

### Run Log — After

<!-- Same format, same five criteria, three runs each.
     `python run_eval.py --label after` -->

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Retrieved chunk contains the answer | 4 of 5 |  |  |  |  |
| 2. Every answer names a source | 5 of 5 |  |  |  |  |
| 3. Gate stops out-of-corpus questions | 4 of 5 |  |  |  |  |
| 4. | | | | | |
| 5. | | | | | |

**Did it help?**

<!-- Say plainly whether it did, and how you know. If it made things worse,
     say that — a change that backfired, honestly reported, earns full credit
     and is more interesting than one that worked. What matters is that you can
     tell.

     Milestone 4. -->

## What's Still Broken

<!-- For each criterion still missed after your fix: what you'd do about it,
     and why you stopped where you did.

     "I ran out of time" is fine if it's true. Pretending nothing is left is
     not.

     Milestone 5. -->

## What I'd Do Differently

<!-- Knowing what you know now — which of your five criteria would you write
     differently, and why?

     Milestone 5. -->
