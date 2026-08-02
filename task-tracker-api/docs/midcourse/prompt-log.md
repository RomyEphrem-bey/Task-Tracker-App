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
