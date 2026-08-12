# My AI Coding Playbook

## 1. When I reach for AI first

> - [Task shapes where AI is my starting point]: ___  Well-defined coding tasks such as generating data models, scaffolding CRUD endpoints, adding business rules, adding business rules, refactoring focused sections, drafting tests,and producing repo-grounded plans or reviews.
> - [Signals that make AI useful immediately]: ___ The task has clear context, references the actual files, focuses on one task at a time, and specifies exact expected behavior, constraints, and output format so the result can be verified immediately. The appropriate context strategy can be clearly identified for the task.
> - [What I want AI to produce first]: ___ A focused first draft or implementation for one clearly defined task that I can inspect and verify before moving to the next step.
>
> Summary: “Ask → Inspect → Run → Test → Refine.” Good prompts reference actual files, focus on one task at a time, specify exact expected behavior, and include constraints about what AI should not change. AI produces the draft; I remain responsible for reviewing and verifying it.

---

## 2. When I do not reach for AI

> - [Task shapes I handle without AI]: ___Running verification steps and directly checking observable results, such as executing the application, using curl or Swagger, inspecting browser/DevTools behavior, running pytest, and performing Break Tests.
> - [Information or contexts that rule AI out]: ___Situations where AI lacks the relevant project files, requirements, evidence, or constraints. In those cases, I first gather and provide the missing context rather than letting AI guess or make unsupported assumptions, or when the information contains secrets, credentials, PII, real customer data, or private production logs.
> - [Situations where direct investigation comes first]: ___When something fails or behaves unexpectedly, I first reproduce the problem and collect evidence such as status codes, response bodies, console or Network tab messages, diffs, and pytest failure output. I then give that evidence to AI for a focused diagnosis or correction.In addition investigation would comes first when verifying the changes AI has made to confirm the implementation works as expected and that no additional, unrelated, or unrequested changes were made.

---

## 3. My non-negotiables

> - [Boundary an AI tool must not cross]: ___ AI must not make unrelated or unrequested changes, invent project structure or dependencies, or override established requirements and business rules. The prompt library repeatedly uses DO NOT constraints specifically to prevent changes to the wrong files or parts of the application.
> - [Evidence or verification I require]: ___I require observable proof that the generated changes work as expected through code review and the appropriate verification method, such as import checks, curl/Swagger checks, pytest, and Break Tests—not simply accepting AI’s claim that the implementation is correct.
> - [Project constraint AI-generated work must preserve]: ___AI-generated work must preserve the existing project structure, files, conventions, interfaces, and previously verified behavior, while modifying only what the task requires.

---

## 4. My review rules

> - [What I check in every AI-assisted change]: ___I review the diff to confirm the change matches the requested behavior, follows the existing project structure and conventions, and does not introduce unrelated or unrequested changes. This reflects the course rule that generated code must be reviewed before it is applied.
> - [What must be true before I accept a change]: ___The change must meet the stated requirements and constraints, preserve previously working behavior, and pass the relevant verification or tests before I move on. I must understand the AI-generated code I accept and be able to explain what it does.
> - [What requires additional review or testing]: ___Changes involving validation, business rules, error handling, status codes, or other behavior that could affect multiple parts of the application require additional testing, including edge and failure cases where appropriate. The module specifically verifies validation and business rules and then uses Break Tests to prove that the tests actually detect broken behavior.

---

## 5. What I am still figuring out

> - [Workflow question I have not resolved]: ___How to decide the right level of task size and context to give AI so that I get useful results without making the change too broad or difficult to review.
> - [AI capability or use case I am evaluating]: ___How effectively AI can help diagnose and debug problems from concrete evidence, rather than only generating an initial implementation.
> - [Boundary or habit I may revise]: ___How much code and context I give AI at once, adjusting it based on the task shape, risk, and how easily I can review and verify the result.

---

## Decision Card

> - For a new feature I reach for: ___AI for a focused first draft.
> - For code review I reach for: ___AI for diff and regression review.
> - For debugging I reach for: ___AI with exact errors, logs, and failing tests.
> - For infrastructure I reach for: ___AI for drafting, then direct verification(Claude Code for terminal-based Docker/CI work).
> - For planning and governance I reach for: ___AI for options; I make the decision(Codex App for repo-grounded planning and governance).
> - I will never paste ___Credentials, tokens, PII, Customner data or confidential data.
> - My one rule is: ___AI proposes; I inspect, verify, and decide.
