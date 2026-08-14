# My AI Coding Playbook

## 1. When I reach for AI first
Well-defined coding tasks: generating data models, scaffolding CRUD endpoints, adding business rules, refactoring a focused section, drafting tests, or producing a repo-grounded plan or review. AI is useful immediately when the task has clear context, references actual files, sticks to one thing at a time, and states the expected behavior, constraints, and output format precisely enough that I can verify the result right away. What I want out of that first pass is a focused draft I can inspect before moving to the next step — not a finished feature.

Summary: **Ask → Inspect → Run → Test → Refine.** Good prompts reference actual files, focus on one task, specify exact expected behavior, and say what AI should *not* change. AI produces the draft; I stay responsible for reviewing and verifying it.

## 2. When I do not reach for AI first
Running verification and reading the result myself: executing the app, hitting endpoints with curl/Swagger, watching browser DevTools, running pytest, doing break tests. AI is ruled out when it doesn't have the real project files, requirements, or evidence in front of it — I gather that context myself rather than let it guess — and always when secrets, credentials, PII, or real customer data would have to touch the conversation to do so.

When something fails, I reproduce it and collect evidence first — status codes, response bodies, console/Network output, diffs, pytest failures — then hand AI that evidence for a diagnosis, rather than describing the symptom from memory. The same applies after AI makes a change: I verify it myself before trusting it, the way I boundary-tested the new length limits at exactly the documented values and one past them, rather than taking the passing test suite as the whole story.

## 3. My non-negotiables
AI must not make unrelated or unrequested changes, invent project structure or dependencies, or override established requirements and business rules — my prompts use explicit DO-NOT constraints for exactly this reason. I require observable proof a change works — code review plus the right verification (import check, curl/Swagger, pytest, break test) — never just AI's say-so. And AI-generated work has to preserve the existing structure, conventions, interfaces, and previously verified behavior, changing only what the task actually requires.

Never paste: credentials, tokens, PII, customer data, or anything confidential.

## 4. My review rules
Every AI-assisted change gets read as a diff: does it match what was asked, does it follow existing conventions, did anything unrequested sneak in. Before I accept it, it has to meet the stated requirements, leave previously working behavior intact, and pass the relevant tests — and I have to be able to explain what the code does, not just that it runs. Anything touching validation, business rules, error handling, or status codes gets extra scrutiny, including edge and failure cases, because that's where a plausible-looking change is most likely to be quietly wrong.

That last point held up in the final project's AI review mini-log: one AI comment claimed a length check could be bypassed with whitespace padding. It was wrong — re-reading the code showed the check ran against the already-stripped value — but it looked plausible enough that I wouldn't have caught it without going back to the actual lines. Grading each AI comment Useful/Noise/Wrong instead of just applying or ignoring it is now a habit, not just a course exercise.

## 5. What I am still figuring out
How to size the task and context I give AI so results are useful without the change becoming too broad to review properly. How well AI actually helps with diagnosis rather than just first-draft generation. And where to redraw the line on how much I hand over at once, based on task shape, risk, and how easily I can check the result.

One concrete instance from the final project: grading the CI-pinning finding (mutable tag vs. SHA-pinned actions) as Noise rather than Valid was a judgment call about *this repo's* actual risk, not a generic security rule — I'm still working out how to make that severity-vs-context call consistently instead of case by case.

---

## Decision Card

> - For a new feature I reach for: ___AI for a focused first draft.
> - For code review I reach for: ___AI for diff and regression review.
> - For debugging I reach for: ___AI with exact errors, logs, and failing tests.
> - For infrastructure I reach for: ___AI for drafting, then direct verification(Claude Code for terminal-based Docker/CI work).
> - For planning and governance I reach for: ___AI for options; I make the decision(Codex App for repo-grounded planning and governance).
> - I will never paste ___Credentials, tokens, PII, Customner data or confidential data.
> - My one rule is: ___AI proposes; I inspect, verify, and decide.
