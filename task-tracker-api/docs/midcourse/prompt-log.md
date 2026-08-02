# Prompt Log — Feature 1: Tags / Labels

For each entry: the prompt sent, a summary of what the AI returned, and what was accepted, edited, or rejected.

## 1. Scope-setting / kickoff prompt

**Prompt:**
> As a QA, I need to continue developing our Task Tracker App as requested below. As a start I need u to make sure you have everything to help me, don't do anything before I tell u what to do — we need to keep track of the below requested docs, I will be selecting the Features, for now just tell me if everything is clear or u need extra things.

**AI returned:** Confirmation it had the project archive, would not inspect/modify/run anything until told, flagged an ambiguity in the brief (`docs/` vs `docs/midcourse/` for submission), and listed everything it understood needed tracking (branch name, baseline, user stories, ADR, prompt log, ≥4 new tests, ≥2 break tests, reflection).

**Accepted / edited / rejected:** Accepted in full — this became the working checklist for the whole project. The `docs/midcourse/` ambiguity call was accepted as the correct path.

---

## 2. Feature selection + user story generation prompt

**Prompt:**
> So As a QA doing a mid course project I will select the second feature option "Tags/Labels" as a first we do not need to write any code, we need to prepare 3 to 5 user stories for the selected feature having the following format... Now generate 5 more stories in the same format.

**AI returned:** Five user stories with acceptance criteria (multi-tag assignment, trimming/whitespace rejection, editing tags via PATCH, tags-optional, tag filtering).

**Accepted / edited / rejected:** Stories 2-5 accepted as-is. Story 1 was **rejected in its first form** — it only said "assign multiple tags" without stating tags could be created *at task-creation time*, which was a requirement. This became prompt #3.

---

## 3. Weak prompt → stronger prompt (architecture planning)

**Weak draft (rough ask before refinement, not what was actually sent):**
> now I need to have the plan so we can add the feature into the existing App

This would have been too open-ended — no constraints on scope, no required deliverables, no format, high risk of the AI proposing an over-engineered design (new endpoints, a database, etc.).

**Strong prompt actually sent:**
> ...Constraints: 1- this is not a production software 2- keep the tech stack simple and well documented 3- do not change or add new features unless it's requested 4- do not modify existing app features 5- Do not suggest microservices, Docker or cloud deployment. Propose two different lightweight architectures (A and B). For each one provide: Tech stack (specific libraries with versions)... Files that should be modified... Data model sketch... Do not write any code, only plan. Three main trade-offs compared to the other option.

**AI returned:** Two full architecture proposals (A: tags embedded on task; B: separate tag catalogue with associations), each with tech stack, files to modify, data model, trade-offs, and a final recommendation (A).

**Accepted / edited / rejected:** Architecture A accepted and implemented. Architecture B rejected as unnecessary complexity for the requested scope (see `mini-adr.md`).

---

## 4. Story 1 correction prompt

**Prompt:**
> So I need u to mention specifically in story 1 that on creation of Tasks, Tags can be created & assigned, do not change other userstories keep them aside

**AI returned:** A revised Story 1 explicitly stating tags can be created and assigned during task creation, with the other four stories left untouched as instructed.

**Accepted / edited / rejected:** Accepted. This is the AI-assumption correction recorded in `user-stories.md` — the AI's first draft of Story 1 under-specified the creation-time requirement, and this was caught and fixed before moving to implementation.

---

# Prompt Log — Feature 2: Task Comments

## 5. Feature selection prompt

**Prompt:** Presented with four remaining core feature options (due dates, task comments, search + filters, activity log) and asked which to build second.

**AI returned:** A short comparison of scope/effort/visibility for each option.

**Accepted / edited / rejected:** Task Comments selected.

---

## 6. User story narrowing prompt

**Prompt:**
> only I will pick some of the user stories Story 1, Story 2, Story 3 and story 5

**AI returned:** Confirmation that Story 4 (blank/whitespace comment rejection) would be dropped since it was already covered by Story 1's acceptance criteria, and the remaining four were appended to `user-stories.md`.

**Accepted / edited / rejected:** Accepted — Story 4 dropped as redundant scope, not as a gap.

**Original Story 4 (proposed, not selected):**
> **As a** team member, **I want** blank or whitespace-only comments rejected **so that** the discussion history isn't cluttered with meaningless entries.
>
> **Acceptance Criteria:**
> - Comment text is trimmed before validation.
> - A comment that is empty after trimming returns 422.
> - Valid comment text with incidental leading/trailing whitespace is stored trimmed.
>
> Not selected as a standalone story because Story 1's acceptance criteria already require "A comment requires non-blank text; whitespace-only or empty text returns 422" — this story's requirements are a duplicate, not a gap.

---

## 7. Architecture decision override

**Prompt:**
> keep both architectures and in the summary do a comparision table and pick architecture B

**AI returned:** A comparison table of Architecture A (comments embedded on the task, matching the Tags pattern) vs. Architecture B (separate `_comments` store keyed by comment ID). The AI's own recommendation had been Architecture A, for consistency with Tags and to avoid extra cleanup-on-delete logic.

**Accepted / edited / rejected:** **AI recommendation rejected.** Architecture B was chosen deliberately despite being the larger change, to keep comment storage decoupled from the task record. This is recorded as a rejected-AI-suggestion decision in `mini-adr.md`.

---

## 8. Delegated technical decision

**Prompt:**
> u can pick as a QA i'm not really familiar with both route so pick in this case only whatever u want

**Context:** Architecture B's natural delete route would be flat (`DELETE /comments/{comment_id}`), which couldn't satisfy Story 3's "missing task returns 404" requirement and would be the only non-nested route in the API.

**AI returned:** Recommended and used a nested route instead — `DELETE /tasks/{task_id}/comments/{comment_id}` — keeping Architecture B's storage but aligning the URL shape with the rest of the API.

**Accepted / edited / rejected:** Accepted as proposed; recorded in `mini-adr.md`'s "Route design note."

---

## 9. Architecture reversal — back to Architecture A

**Prompt:**
> let s pick Architecture A and comment this as a record in the related document that this change wasn't accepted by AI and my decision is to follow Architecture A

**Context:** Architecture B was, at this point, the AI-selected active architecture — a `models.py` draft implementing B had already been proposed and was awaiting approval. The AI had not proposed switching back to A.

**Accepted / edited / rejected:** This is a human-directed decision reversal, explicitly not an AI suggestion. Recorded as such in `mini-adr.md`'s "Decision history."

---

## 10. Implementation constraints prompt

**Prompt:**
> so now we nned to follow Adr A for feature 2. Constraints: DO not change initial code, DO not break the Code, Make sure to apply first the backend then once applied we will move into writing the testing functions. Make sure to not make assumptions. DO not change the existing codes unless approved, explain everything step by step remember I'm just a QA

**AI returned:** A proposed `app/models.py` addition for Architecture A: a new `Comment` model, a new `CommentCreate` model with a trim/reject-blank validator (matching the existing title/tag validator pattern), and a single new `comments` field added only to `TaskResponse`. No existing class, field, or validator was touched. Deliberately left `comments` out of `TaskCreate` and `TaskUpdate`, since no approved user story asks for setting comments at task-creation time or through the general edit PATCH — comments are only added/listed/deleted through their own dedicated actions (Stories 1-3).

**Accepted / edited / rejected:** Accepted, pending one confirmation (see prompt #11 below) before being applied to disk.

---

## 11. Design confirmation — comments only in edit modal

**Prompt:**
> the comment field is only available in edit modal not on create

**AI returned:** Confirmation that this matches exactly what had been proposed (no `comments` field on `TaskCreate`), so the `models.py` change was applied as drafted.

**Accepted / edited / rejected:** Accepted as-is. The full pytest suite (23 tests) was re-run immediately after applying the change and confirmed no regressions — the addition is purely additive.

---

## 12. Storage layer prompt — list/add/delete comment behavior

**Prompt:**
> So now let s move specifically into supporting list/add/delete comment behavior, same constraint as previous prompt

**AI returned:** Before writing any code, the AI raised one open design question rather than assuming an answer: should adding/deleting a comment bump the task's `updated_at` timestamp, the way the existing PATCH endpoint always does? The user chose **no** — `updated_at` should only reflect changes to the task's own fields, not its comments. The AI then proposed three new `app/storage.py` functions (`add_comment`, `get_comments_for_task`, `delete_comment`), all built around the existing `_tasks` dict and the same "copy the task, don't mutate in place" pattern already used by `update_task()`. No existing function was changed.

**Accepted / edited / rejected:** Accepted and applied as proposed. Full pytest suite (23 tests) re-run immediately after and confirmed no regressions.

---

## 13. Routes layer prompt — reject blank / list / delete / 404 handling

**Prompt:**
> now let s modify specifically the functions to handle user story 1 related to "eject blank comment, list comments for a task, delete comment, 404 for missing task/comment." same constraints as previous prompt and do not forget to to log

**AI returned:** Pointed out that "reject blank comment" was already fully handled by the `CommentCreate` validator from Step 1, so no new code was needed for that part. Proposed three new `app/main.py` routes — `POST/GET /tasks/{task_id}/comments` and `DELETE /tasks/{task_id}/comments/{comment_id}` — each calling the Step-2 storage functions and translating their `None`/`False`/`True` results into 404s or success responses, matching the existing route style exactly (same `HTTPException` pattern as `update_task_route`/`delete_task`). No existing route was changed.

**Accepted / edited / rejected:** Accepted and applied as proposed. Full pytest suite (23 tests) passed with no regressions, and a manual smoke test via `TestClient` confirmed: trimming works, a blank comment returns 422, a missing task returns 404 on add/list/delete, a missing comment on a real task returns 404, a successful delete returns 204, and the comment list correctly reflects the deletion afterward.

---

## 14. Comment count on cards — sequencing check

**Prompt:**
> So now let s add a count on cards, that will count on each task the number of comments added, same as previous prompt for the constraints

**AI returned:** Flagged that this request skips ahead of the stated backend → tests → frontend order (pytest tests for Stories 1-3 hadn't been written yet), and noted the count itself needs no backend change since `TaskResponse` already returns the full `comments` list. The user chose to write the pytest tests first, as originally planned, before touching the frontend.

**Accepted / edited / rejected:** Card-count implementation deferred; proceeded to write `tests/test_comments.py` instead (prompt #15).

---

## 15. Backend test-writing prompt

**Context:** Continuation of prompt #14's decision to write tests before the frontend. Ten pytest tests were drafted covering Stories 1-3 (add/trim/reject-blank/missing-task-404, list/empty/missing-task-404, delete/missing-task-404/missing-comment-404) in a new `tests/test_comments.py`.

**Follow-up prompt:**
> why covering only stories from1 to 3?

**AI returned:** Explained that Story 5 (comment count) has no dedicated backend endpoint, so it had been left out of the pytest file on the assumption it belonged only to a manual browser check later. Also identified a legitimate backend-testable piece of Story 5 that had been overlooked — confirming `GET /tasks/{task_id}` reflects the correct `comments` count after add/delete — and asked whether to add it rather than assuming either way.

**Accepted / edited / rejected:** User chose to leave Story 5 to the manual browser check only, keeping `test_comments.py` scoped strictly to Stories 1-3. The 10 tests were applied as originally drafted; full suite (33 tests: 23 existing + 10 new) passed.

---

## 16. Break Test prompt — Task Comments

**Prompt:**
> so not let's try breaking 1 test by adding an acceptance to having a blank comment & re rerun the test to see a failure & let s document this

**AI returned:** A step-by-step plan: temporarily remove the blank-rejection check from `CommentCreate`'s `_text_not_blank` validator in `app/models.py`, re-run `test_add_comment_blank_returns_422` to confirm it fails, revert the validator, re-run the full suite to confirm all tests pass again, then document the result.

**Result:** With the validator weakened, the test failed exactly as expected — `assert 201 == 422` (a blank comment was accepted instead of rejected). This confirmed the test genuinely guards the behavior it claims to. The validator was reverted immediately, and the full suite (33 tests) passed again.

**Accepted / edited / rejected:** Accepted and executed as proposed. Recorded as a Break Test in `verification.md`'s Feature 2 section — this is a different break-test style than Tags' (which probed a real, unfixed limitation with adversarial input); this one deliberately breaks the implementation to prove the test suite would catch a regression.
