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

This is a RAG system that answers questions about student life at a university, using `campus_life`, a set of 88 short student-written posts about dining, housing, admin rules, and courses. It retrieves the most relevant post for a question and answers using only the content, citing the source file. If a question isn't covered by the documents, a relevance gate catches it and the system says so rather than guessing. Example questions it can answer include things like "What is the expected workload outside of class for a week in CS 210?" and "What are the wait times like at Kestrel Commons during lunch?"
<!-- Three or four sentences. Which corpus you picked, and the kinds of
     questions your system answers. Write it for someone who has never seen
     this repo.

     Milestone 5. -->

## Chunking Strategy

**Chunk size:** 600
**Overlap:** 60

Document lengths across all 88 campus_life files run from 178 to 563 characters, median 315, and every single post fits under 600, so that's set just above the longest real document rather than a round generic number like 800. The intent is that whole posts stay whole.

I checked whether paragraph structure argued for splitting anyway. Most posts have 3-5 blank-line-separated paragraphs, but the first is almost always a bare one-line title ("On the add/drop deadline", "Re: Halden Hall"), and the rest is 1-2 short body paragraphs building one point (e.g. the CS 210 workload post: "8-10 hrs/week" then "front-loaded"). Splitting on blank lines would strand a title on its own and separate a claim from its immediate qualifier, which is worse than keeping the post as one chunk.

The one real exception is the dining-hall `_followup` files, which do stack two independent facts (wait time + closing time, in `dining_halden_hall_followup.txt`). I'm accepting that as the legitimate miss already called out in criteria.md #4, rather than building a splitting rule around ~7 files that would break the other 80+ posts that are genuinely one thought.

Overlap of 60 (~10% of chunk size) exists only as a safety net for the rare case a document exceeds 600 characters, and it should almost never fire on this corpus, but it avoids a hard cutoff with no shared context if a post grows past the cap later.


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

(best distance 0.201, cutoff 0.6). Retrieval also pulled in `housing_aldridge_hall.txt`, `housing_aldridge_hall_laundry.txt`, and `housing_calder_annexe.txt`, near-identical sibling docs with different prices ($1.75/$1.50 and $2.00/$1.75), and the model still attributed the right numbers to the right building.

**My relevance cutoff:**

I set `THRESHOLD = 0.6` in `config.py` (the starter default). My five in-corpus questions had best distances of 0.175-0.372, and the five `OUT_OF_SCOPE` questions had best distances of 0.825-0.934, a clean gap from about 0.37 to 0.82 with no overlap between the two groups. 0.6 sits in the middle of that gap rather than hugging either edge, which gives the most margin against a future question landing close to either group's boundary.

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

**Unit 2**

**1.**

I asked Claude to help diagnose which pipeline stage caused the criterion 4 miss, and to look for a pattern across the failing chunks instead of explaining each one separately. It traced the miss to one mechanism in `chunker.py::split_documents`: keeping a whole post as one chunk based on length alone, never how many separate things the post talked about. It showed that failures in four different categories, admin, health, housing, and orientation, were all the same mechanism and not four unrelated problems. That reframing changed what I fixed. Instead of treating this as a handful of one-off bad chunks, I rewrote the one length-only rule the diagnosis pointed at. Doing this improved criterion 4's numbers, even though it still missed the target. 


## Stretch: Metadata Filtering

**Doing this one.** Retrieval can be narrowed by `category`, a metadata field derived from the part of each filename before its first underscore (`housing_calder_annexe.txt` → `"housing"`), stored on every chunk at index time in `store.py::build_index` and applied as a Chroma `where` clause in `store.py::search`. `python app.py retrieve "..." --category housing` (or `admin`, `dining`, `course`, `money`, etc.) is the CLI entry point.

**Same query, with and without the filter:**

Question: *"What does it cost?"*

No filter (`python app.py retrieve "What does it cost?" --top-k 5`):

```
#   distance   source                           preview
----------------------------------------------------------------------------------------------------
1   0.5970     housing_calder_annexe.txt        Calder Annexe — what it's actually like  Second-year...
2   0.6954     admin_printing_quota.txt         On the printing quota  Every student gets $30 of pri...
3   0.7093     money_textbooks.txt              Textbooks without paying full price  The library hol...
4   0.7146     housing_fenwick_court.txt        Fenwick Court — what it's actually like  Just finish...
5   0.7191     housing_innisfree_hall.txt       Innisfree Hall — what it's actually like  Transferre...
```

With `--category housing` (`python app.py retrieve "What does it cost?" --top-k 5 --category housing`):

```
#   distance   source                           preview
----------------------------------------------------------------------------------------------------
1   0.5970     housing_calder_annexe.txt        Calder Annexe — what it's actually like  Second-year...
2   0.7146     housing_fenwick_court.txt        Fenwick Court — what it's actually like  Just finish...
3   0.7191     housing_innisfree_hall.txt       Innisfree Hall — what it's actually like  Transferre...
4   0.7325     housing_aldridge_hall.txt        Aldridge Hall — what it's actually like  I lived her...
5   0.7492     housing_morrow_house.txt         Morrow House — what it's actually like  Just finishe...
```

**What changed:** unfiltered, the top result was already `housing_calder_annexe.txt`, but positions 2-5 pulled in one admin doc (printing quota) and one money doc (textbooks) that happen to sit near "cost" in embedding space even though they're not about housing. With `--category housing`, those two get excluded before the top-k cutoff, so instead of leaving 2 of 5 slots, the filter frees up those slots for other housing posts (`aldridge_hall.txt`, `morrow_house.txt`) that didn't make the unfiltered top 5 at all. The single best match doesn't move, since it was already in-category, but every question where the best match lands outside the category the user meant would benefit.

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
| 1. Retrieved chunk contains the answer | 4 of 5 | 5/5 |5/5 | 5/5 | met |
| 2. Every answer names a source | 5 of 5 | 5/5 | 5/5 | 5/5 | met |
| 3. Gate stops out-of-corpus questions | 4 of 5 | 5/5 | 5/5 | 5/5 | met |
| 4. Sampled chunks hold one fact, not two|4 of 5 | 1/5 | 2/5 | 2/5 | missed |
| 5. Cited source is the specific document | 4 of 5 | 5/5 | 5/5 | 5/5 | met |


**Covers criteria 1 and 2:** the retrieved chunk contains the answer, and the answer names a source.

### What are the wait times like at kestrel commons during Lunch? (Run 1)
- Best distance: 0.1768 (passed the gate)
- Sources retrieved: dining_halden_hall_followup.txt, dining_kestrel_commons.txt, dining_kestrel_commons_followup.txt, dining_north_kitchen_followup.txt, dining_the_ridgeway_cafe_followup.txt

```
At Kestrel Commons, wait times are 20 to 25 minutes between 12:15 and 1:00, and under 5 minutes before 11:45. 

Source: `dining_kestrel_commons.txt` (and `dining_kestrel_commons_followup.txt`)
```


### Criterion 3 evidence: "What is the capital of Mongolia?"

Produced by `store.py::search` (retrieval) and `gate.py::check` (the refusal decision). This is one of the five `OUT_OF_SCOPE` questions; the gate never lets it reach the model.

```
$ python app.py ask "What is the capital of Mongolia?"
  (best distance 0.825, cutoff 0.6)

I don't have enough information about that.

0 model calls this session
```

### Criterion 4 evidence: three random samples of 5 chunks

Produced by `chunker.py::split_documents`. Each run draws 5 chunks at random from all 88 and checks whether each one holds only one countable fact (a number, deadline, or dollar amount) rather than two bundled together.

**Run 1 (1 of 5 passed):**

```
[PASS] housing_aldridge_hall_noise.txt#0
Noise levels in Aldridge Hall

Asked about this a lot so writing it down. Quiet floors on 3 and 4 are genuinely enforced.

If you're someone who needs quiet to work, the library is open until 2am during term and that's what most people in this building end up doing.
```
```
[FAIL] admin_add_drop_deadline.txt#0
On the add/drop deadline

You can add a course through the end of the second week. Dropping is a longer window — through the end of week six — but a drop after week two shows as a W on your transcript. Nothing anywhere on the registrar's site says this plainly, and students find out from each other.
```
```
[FAIL] dining_the_ridgeway_cafe_followup.txt#0
Re: The Ridgeway Café

Adding to what people have said about The Ridgeway Café. The wait figure of 10 to 15 minutes at 12:30 matches what I've seen. If you're trying to eat between classes, go before 11:45 and it's a different building entirely.

Also worth saying: seating is tight; about 40 seats for a building of 900. Nobody tells you this at orientation.
```
```
[FAIL] health_center.txt#0
The health centre

Walk-in hours are 8am to 11am; everything after that is by appointment and appointments run about a week out. If something is urgent, go at 8am and wait rather than booking.

Counselling is separate, in the same building, and has its own intake process with a shorter wait than people expect — usually three or four days for a first session.
```
```
[FAIL] housing_calder_annexe.txt#0
Calder Annexe — what it's actually like

Second-year here. Built 2003. Rooms are mostly singles, some doubles, in clusters of six around a lounge.

The good: the cluster lounges mean you meet people without having to try.

The bad: the singles are small — about 90 square feet — and the desks are fixed.

Laundry costs $2.00 wash, $1.75 dry, app-based. On noise: depends entirely on your cluster; there's no building-wide pattern.
```

**Run 2 (2 of 5 passed):**

```
[PASS] admin_dining_dollars.txt#0
On the dining dollars

Declining balance — what everyone calls dining dollars — rolls over from the autumn semester to the spring, but not from spring to the following autumn. Whatever is left in May disappears.
```
```
[PASS] course_stat_150_exams.txt#0
STAT 150 Applied Statistics — assessment

Three equally weighted midterms, no final. No curve, but the lowest midterm is dropped.

The dropped midterm makes the first one low-stakes; use it to learn the format.
```
```
[FAIL] dining_the_atrium_followup.txt#0
Re: The Atrium

Adding to what people have said about The Atrium. The wait figure of no queue matches what I've seen. If you're trying to eat between classes, go before 11:45 and it's a different building entirely.

Also worth saying: picked clean by 1:15 and not restocked again until the next morning. Nobody tells you this at orientation.
```
```
[FAIL] dining_the_ridgeway_cafe_followup.txt#0
(same chunk as Run 1 — reproduced above)
```
```
[FAIL] study_group_rooms.txt#0
Booking a group study room

Rooms book two weeks ahead through the library site, in two-hour blocks, maximum two blocks per person per week. The limit is per person, so a group of four can chain together eight hours if they coordinate.

Rooms 210 and 211 have whiteboards that actually erase. The others don't and no amount of scrubbing helps.
```

**Run 3 (2 of 5 passed):**

```
[PASS] admin_dining_dollars.txt#0
(same chunk as Run 2 — reproduced above)
```
```
[PASS] course_engl_205_exams.txt#0
ENGL 205 Writing for the Sciences — assessment

No exams; a portfolio of six revised pieces. Not curved.

The portfolio is graded on revision, so keep your drafts — you're marked on the distance travelled.
```
```
[FAIL] dining_halden_hall.txt#0
Halden Hall

I lived here my sophomore year. Wait times: rarely more than 8 minutes, even at noon. The thing worth going for is soup rotation, and the bread is baked on site. The thing to know is that closes at 7:00pm, which catches people out.

Hours are 7:30am to 7:00pm weekdays, closed Sundays. Costs one meal swipe, or $10.00 cash.
```
```
[FAIL] housing_old_brewhouse_laundry.txt#0
Laundry in Old Brewhouse

Machines take $1.50 wash, $1.50 dry, coin only, and the machines are old. There are eight washers and six dryers for the building, which is the wrong ratio and means the dryers back up on Sunday evenings.

Best time to do laundry here is Tuesday or Wednesday morning. Sunday after 6pm you will wait.
```
```
[FAIL] orientation_what_matters.txt#0
What actually matters in orientation week

Most of it is optional and framed as though it isn't. The two sessions worth going to are the one where you meet your academic adviser and the library walkthrough, because both save you time later.

The club fair is genuinely useful but goes on for four hours and you only need the first forty minutes.
```

Three independent samples land at 1/5, 2/5, and 2/5, consistently below the 4-of-5 target, and not limited to the dining follow-up files my Milestone 3 write-up flagged. Admin, health, housing, and orientation posts bundle multiple facts just as often.

### Criterion 5 evidence: "How much does laundry cost at Innisfree Hall?"

Produced by `store.py::search` (retrieval) and `generate.py::answer_from_chunks` (the citation). Chosen over the Kestrel Commons example because retrieval actually pulled in sibling documents here, so this is a real test of criterion 5 rather than an easy case with no siblings competing.

```
Laundry at Innisfree Hall costs $1.75 for a wash and $1.75 for a dry.

Sources: `housing_innisfree_hall_laundry.txt` and `housing_innisfree_hall.txt`
```

(best distance 0.201, cutoff 0.6). Retrieval also pulled in `housing_aldridge_hall.txt`, `housing_aldridge_hall_laundry.txt`, and `housing_calder_annexe.txt`, near-identical sibling docs with different prices ($1.75/$1.50 and $2.00/$1.75), and the model still attributed the right numbers to the right building.

## Verdicts

<!-- MET or MISSED for each of the five, against the target you wrote last
     unit — not a new one. Plus a sentence on how you decided. That sentence
     matters most where it was close.

     If your target said 4 of 5 and your runs came out 4, 3, 4, that's a MISS.
     The target has to hold, not show up occasionally.

     Milestone 2. -->

| # | Criterion | Verdict | How I decided |
|---|---|---|---|
| 1 | Retrieved chunk contains the answer | met | All 3 runs came back 5/5 for the questions, which exceeded the 4 of 5 target. |
| 2 | Every answer names a source | met | Every answer in all 3 runs cited a source. 5/5 matching the 5 of 5 target exactly. |
| 3 | Gate stops out-of-corpus questions | met | The gate refused 5/5 out of scope questions, which exceeds the 4 of 5 target. |
| 4 | Sampled chunks answer one question, not two | missed | I revised this criteria to fix the wording that turned out to be ambiguous/unmeasurable, the results only changed to have all 3 runs be 2/5 still a miss, but easier for someone to understand what this criteria is supposed to be. The full revision and reason can be found in criteria.md. |
| 5 | Cited source is the specific document | met | All 3 runs cited the specific correct document source, not a sibling document. 5/5 which exceeds the 4 of 5 target. |

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

**Criterion 4 - chunking stage:**

`chunker.py::split_documents` keeps a whole post as one chunk as long as it's under 600 characters (lines 108-121), and the only thing it checks is length, not how many separate things the post is talking about. I wrote that rule expecting one edge case, the dining `_followup` files pairing a wait time with a closing time, and said as much in criteria.md #4.

The three runs show it's not just those ~7 files. `admin_add_drop_deadline.txt` bundles the add deadline and the drop deadline, `health_center.txt` bundles walk-in hours and counselling intake, `housing_calder_annexe.txt` bundles a room description, a laundry price, and a noise note, and `orientation_what_matters.txt` bundles the adviser meeting and the club fair. My Milestone 3 assumption, that only the dining follow-up files stack two facts, underestimated how many posts actually have that structure.

Different categories, same cause: a post just needs 2-3 body paragraphs and still fit under 600 characters, and nothing about the chunker looks past its length to notice that. It's one mechanism producing the miss repeatedly, not five unrelated ones.

## The Improvement

**What I changed:**
Rewrote `chunker.py::split_documents` so it chunks on paragraph boundaries instead of keeping a whole post as one chunk if it is under 600 characters. Each post's paragraphs, separated by blank lines, become their own chunk, except the title which stays merged with the first body paragraph. Oversized paragraph fallback is still there for the rare case where a paragraph exceeds 600 characters. I re-indexed under a second variant (paragraph) so the original index and its results stay intact for comparison. 88 posts now produce 183 chunks. 

**Why I picked it:**
This follows directly from the Diagnoses section: the miss traced to `split_documents` only checking a post's length, never how many separate things it talked about. So splitting on the paragraph boundaries the corpus already uses to separate one thought from the next attacks that original mechanism directly instead of touching retrieval or the gate, which weren't implicated.

<!-- Connect it to a specific diagnosis above in one sentence. If you can't,
     you picked a fix because it sounded impressive. -->

### Run Log — After

<!-- Same format, same five criteria, three runs each.
     `python run_eval.py --label after` -->

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Retrieved chunk contains the answer | 4 of 5 | 5/5 | 5/5 | 5/5 | pass |
| 2. Every answer names a source | 5 of 5 | 5/5 | 5/5 | 5/5 | pass |
| 3. Gate stops out-of-corpus questions | 4 of 5 | 5/5 | 5/5 | 5/5 | pass |
| 4. Sampled chunks answer one question, not two | 4 of 5 | 4/5 | 5/5 | 3/5 | missed |
| 5. Cited source is the specific document | 5 of 5 | 5/5 | 5/5 | 5/5 | pass |

**Did it help?**

<!-- Say plainly whether it did, and how you know. If it made things worse,
     say that — a change that backfired, honestly reported, earns full credit
     and is more interesting than one that worked. What matters is that you can
     tell.

     Milestone 4. -->
It helped but not enough to flip the verdict. Criteria 1, 2, 3, and 5 were already at the ceiling, 5/5 every run, before and stayed there, so nothing moved or got worse.

Criterion 4 is where it mattered and changed. Three random samples went from 1/5, 2/5, 2/5 before to 4/5, 5/5, 3/5 after. Two of the three runs now clear the 4 of 5 target, where none did before. But the target has to hold for every run, so run 3's 3/5 keeps the result a miss, just a narrower one.

The remaining failures also converged on one pattern: chunks that pair a fact about a place (a laundry price, a lot's availability) with an unrelated second fact about the same place. Paragraph splitting doesn't fix this, since both facts can still land in the same paragraph. So overall it helped in a measurable way, and narrowed the problem down instead of solving it.

| Criterion | Before | After |
|---|---|---|
| 4. Sampled chunks answer one question, not two | 1/5, 2/5, 2/5 | 4/5, 5/5, 3/5 |


## What's Still Broken

<!-- For each criterion still missed after your fix: what you'd do about it,
     and why you stopped where you did.

     "I ran out of time" is fine if it's true. Pretending nothing is left is
     not.

     Milestone 5. -->

Only criterion 4 is still missed. Criteria 1, 2, 3, and 5 hit their targets in all three runs.

**Criterion 4 - sampled chunks answer one question, not two (4/5, 5/5, 3/5 against a target of 4 of 5):**

Paragraph chunking raised the runs from 1/5, 2/5, 2/5 to 4/5, 5/5, 3/5. The two failures in run 3 show what's left.

`housing_calder_annexe.txt#3` pairs a laundry price with a noise note, and `admin_parking_permits.txt#0` pairs one lot's availability with another lot's and a workaround. In both, the facts share a paragraph, so a blank-line split can't separate them.

**What I'd do about it:** split at the sentence level and group sentences by topic, with a minimum chunk size so a short qualifier doesn't end up as its own chunk.

**Why I stopped:** two reasons. I already needed an extension to finish this project, and a sentence-level split would multiply the 183 chunks and risk separating claims from their qualifiers across the whole corpus. Criteria 1 and 3 are at ceiling, and the paragraph split already pulled the out-of-scope distances closer to the cutoff (Mongolia went from 0.825 to 0.787, still well clear of the 0.6). I didn't want to risk the other four criteria to fix one narrow miss.

One caveat on the measurement: Criterion 4 is a judgment call on a random draw of 5. I moved `admin_housing_lottery.txt#0` from fail to pass because it fully answers the ordering question and the schedule date is incidental. The other call would have changed that run's score.

## What I'd Do Differently

<!-- Knowing what you know now — which of your five criteria would you write
     differently, and why?

     Milestone 5. -->

I would rewrite criterion 4, changing both how I picked the target and how I measure it.

**The target came from too little evidence**

I wrote criterion 4 expecting that only the dining `_followup` files, about seven of them, would bundle two facts, and I justified the 4/5 target on that. Then my own samples showed admin, health, housing, and orientation posts bundle facts just as often. I would instead read a sample across every category before choosing the target, because I predicted the problem from one file type and set a target that was too optimistic.

**The measurement was unstable**

Scoring five random chunks (from 88 before the fix, 183 after) gave 1/5, 2/5, 2/5 and 4/5, 5/5, 3/5 after. Some of that spread is just which chunks got drawn. I would write the definition of "one distinct question" down first, with the wash and dry price rule from my Unit 2 revision. I would then score all 183 chunks, or a fixed set, and set the target as a percentage of chunks. This way calls like `admin_housing_lottery.txt#0` are settled by the definition, not decided after seeing the chunk.
