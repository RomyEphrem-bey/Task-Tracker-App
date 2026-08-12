# Security Review

## AI Findings

| Severity | File:Line | Finding | Suggested Fix | Evidence | Grade | Reason |
|---|---|---|---|---|---|---|
| Medium | `task-tracker-api/app/models.py:47` | Unbounded input and storage permit memory exhaustion. Descriptions, assignees, comments, tag lengths/counts, task count, and comment count have no limits. This is exploitable as denial of service if the API is reachable by untrusted clients. | Add Pydantic length/count constraints, reject oversized request bodies at the server or reverse proxy, paginate task responses, and apply rate or usage limits if deployed. | Only titles have a 200-character limit. `CommentCreate.text` and other strings/lists are unrestricted. Tasks are retained indefinitely in the process-wide dictionary at `task-tracker-api/app/storage.py:8`, while comments are continually appended at `task-tracker-api/app/storage.py:149`. | TODO | TODO |
| Course-scope decision / High if deployed | `task-tracker-api/app/main.py:48` | All task and comment operations are anonymous. Any client that can reach the API can list, create, change, or delete all data. This is intentional under the Module 5 rule forbidding authentication and is not a defect for an isolated teaching environment. | Keep the service bound to a trusted/local environment. Before any real or shared deployment, add authentication plus per-resource authorization and deny anonymous mutation. | Every route through line 355 calls storage directly, with no authentication dependency or authorization check. `GET /tasks` exposes titles, descriptions, assignees, tags, and comments through `TaskResponse`. | TODO | TODO |
| Low | `task-tracker-api/app/main.py:30` | CORS trusts the opaque `null` origin and allows every method and header. `null` can represent local files and sandboxed documents. This does not meaningfully protect or further expose the currently public API, but it becomes dangerous if authorization is later added. | Retain `null` only for explicit local-file development. Use environment-specific, exact HTTPS origins in deployed environments and allow only required methods and headers. | `allow_origins` includes `"null"` at line 36; lines 39–40 use wildcards. `allow_credentials=False` limits present impact. | TODO | TODO |
| Low | `task-tracker-api/requirements.txt:1` | Dependency installation is reproducible only at the top level. Versions are pinned, but hashes and a transitive lock are absent. Test-only packages are also installed into the runtime image. | Maintain a hash-locked dependency set and separate runtime from development/test dependencies so the final image excludes `pytest` and `httpx`. | Exact pins are present, which is good; however the Dockerfile installs the entire file at `task-tracker-api/Dockerfile:11`, including test packages on requirements lines 6–7. No specific dependency CVE is claimed because no current vulnerability scan was run. | TODO | TODO |
| Low | `.github/workflows/ci.yml:15` | CI supply-chain controls are limited. Actions use mutable major-version tags, pip itself is upgraded to the latest release, and CI performs tests only—no dependency, secret, or container scan. | Pin actions to reviewed commit SHAs, use a controlled pip version, and add dependency, secret, and image scanning when production assurance is required. | `checkout@v4`, `setup-python@v5`, and `cache@v4` are tag-pinned rather than SHA-pinned. Line 29 installs an uncontrolled latest pip; lines 32–38 only install dependencies and run tests. | TODO | TODO |
| Low | `task-tracker-api/Dockerfile:4` | The container base is mutable. Rebuilding later may silently use different base-image contents. | Pin the approved `python:3.11-slim` image by digest and automate periodic digest updates and image scanning. | Both build and runtime stages use the floating `python:3.11-slim` tag. | TODO | TODO |
| Clean | `task-tracker-api/app/models.py:47` | Core structural input validation is sound. No injection sink was found in the in-memory backend. | Preserve these controls and add the resource limits described above. | Status and priority are enums; unknown fields are forbidden; titles are stripped, required, and capped; blank tags/comments are rejected. Tests cover invalid enums, unknown fields, blank inputs, and transition rules. | TODO | TODO |
| Clean | `task-tracker-api/frontend/index.html:840` | No stored DOM-XSS path was found in reviewed rendering. | Continue escaping server-controlled values, or migrate rendering to DOM nodes with `textContent`. Add a restrictive CSP at the hosting layer when deployed. | `escapeHtml()` encodes HTML metacharacters, and task/comment values are escaped before insertion at lines 906–918 and 1001–1038. Error text otherwise uses `textContent`. | TODO | TODO |
| Clean | `task-tracker-api/app/main.py:136` | Expected errors are handled without evident sensitive-data leakage. | Consider centralized logging and stable public error codes for production observability. | Missing resources return 404, validation and invalid transitions return 422, and response models constrain output. No debug mode, stack-trace response, secret logging, or raw exception reflection was found. | TODO | TODO |
| Clean | `task-tracker-api/.dockerignore:1` | Secret and container runtime hygiene are generally good. | Preserve these controls. | `.env` is excluded from Docker and Git, is not tracked, and contains no secret-like keys. The image copies only `app/`, uses a multi-stage build, includes a health check, and runs as the non-root `app` user at `task-tracker-api/Dockerfile:37`. | TODO | TODO |

## My Manual Findings

| Severity | File:Line | Finding | Suggested Fix | Reason |
|---|---|---|---|---|

## Reconciliation

### Agreement

### AI-only

### You-only

## Top 3 Unfixed Backlog

| Rank | Finding | Severity | Owner | Next Step |
|---|---|---|---|---|
| 1 | Unbounded input and in-memory storage permit denial of service. | Medium | TODO | Define and implement field, collection, request-size, and pagination limits. |
| 2 | Anonymous access allows all clients to read and mutate all task data if the service is deployed. | Course-scope decision / High if deployed | TODO | Keep deployment isolated; require authentication and authorization before broader exposure. |
| 3 | CI and build inputs are not fully immutable or security-scanned. | Low | TODO | Pin actions and base images immutably, lock dependency hashes, and add appropriate security scans. |
