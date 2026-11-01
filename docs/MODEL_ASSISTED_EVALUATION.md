# Model-assisted engineering evaluation — protocol v0

**Purpose:** Test whether Studio makes a frontier coding model meaningfully better at building or maintaining an actual vibecoded project when the user's request is **natural and underspecified**. The experiment must not reward number of reports, tokens of planning, lifecycle gates or invented enhancements.

## Experimental question

Given the **same model, same pinned repository, tool permissions, time/token budget and user request**, does access to selected Studio engineering knowledge allow a better result than ordinary frontier-model assistance?

## Tasks

Use at least one greenfield and one brownfield case, on independent clean branches or isolated working directories. Suggested first brownfield subject: ScanPlan *prior to* the known Unicode fix, but avoid revealing that vulnerability or its test oracle in the user request, and use an agent without exposure to the prior solution. A sample ordinary vibecoder prompt is:

> Make this command-line tool reliable enough that another developer can actually use it. Keep the current behavior and don't overbuild it.

The request should intentionally omit architecture patterns, tests, UX, input handling, security hygiene, acceptance and documentation details. The experiment team authors **hidden independent acceptance criteria before starting**. A separate evaluator reviews the criteria for relevance, not simply breadth.

The same natural-language request and baseline go to two separate model sessions:
- **Control:** normal model with its coding tools and the project's own context. No specialized Studio knowledge.
- **Studio treatment:** identical model/tools, plus verified task-appropriate Studio knowledge, research IDs and a short cue to identify *necessary* missing engineering considerations and make minimal changes.

Do not leak the treatment's task findings or hidden tests to the control agent. Prefer parallel independent teams and randomized task assignment; a single builder repeating a known solution is contaminated.

## What the model should do

The model examines existing code and conventions, infers product type and intent, identifies meaningful unrequested requirements, selects appropriate practices, edits or builds within scope, and runs proportional tests. Routine work does **not** require a nine-section report or canonical kernel `plan`. Formal risk/acceptance processes remain applicable when necessary.

## Independent evaluation rubric

| Dimension | Measurement |
|---|---|
| Correctness | Hidden acceptance tests, regression suite, integration behavior; report exact failures/skips |
| Product sense | Relevant real-user gaps discovered that a vibecoder omitted; independent reviewer validates necessity |
| Surgical precision | Files touched, unnecessary churn, regressions, avoided rewrite, compatibility preserved |
| UX and maintainability | Usable interface/errors/docs appropriate for this product type, understandable code |
| Security and reliability | Relevant safeguards and negative controls without speculative security claims |
| Avoided feature creep | Unsolicited complexity, unrelated features or unjustified infrastructure counted against result |
| Human burden | Number and quality of clarifying questions, user corrections and external intervention |
| Efficiency | Measured elapsed time, token cost, model/tool spend and revisions to accepted solution |

Publish a per-task score and evidence, including the number of **relevant** omitted concerns inferred versus irrelevant additions. Do not assign a blanket score to every lifecycle stage. The experiment outcome is **better working engineering**, not the count of Studio artifacts.

## Result interpretation

Claim success only for task classes and environments actually measured. When both arms deliver comparable quality, compare actual cost and user burden. When Studio adds overhead without improved outcomes, classify that practice as counterproductive and reduce it. If the treatment creates more files/docs than needed, that is a failure of surgicality even if the documentation is correct.

The 50–75% productivity goal remains a hypothesis. A model's ability to run `studio_kernel` or produce signed receipts **does not establish** this value proposition. Existing 003R selection generalization is NO-GO; do not silently use it as a reliable automatic recommender.

## Minimum reproducibility record

Record pinned SHA, task brief, model/configuration, treatment context IDs, time/token/cost, commands executed, hidden test results, independent reviewer notes, diffs and exclusions. Disclose any contamination, unavailable CI or missing metric. Do not modify other product repositories or the frozen Studio archive to stage the experiment.

**Current status: NOT_RUN.** This is a test protocol, not a claim that either arm completed.
