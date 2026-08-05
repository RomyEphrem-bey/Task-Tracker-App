# User Stories — Feature 1: Tags / Labels

## Story 1
**As a** team member, **I want** to be able to create and assign one or more tags when creating a new task **so that** I can categorize my work from the moment the task is created.

**Acceptance Criteria:**
- One or more tags can be added during task creation.
- Each tag is saved and associated with the newly created task.
- All assigned tags appear on the task card after the task is created.
- A task can still be created without tags if tags are optional.

> **AI assumption corrected:** The AI's first draft of this story only said "assign multiple tags to a task" with no mention of *task-creation time*. It was corrected to explicitly require that tags can be created and assigned at creation, not only added later via edit.

## Story 2
**As a** team member, **I want** tag values to be trimmed **so that** accidental spaces do not create incorrect or duplicate-looking tags.

**Acceptance Criteria:**
- Leading and trailing spaces are removed from every tag.
- A tag containing only spaces is rejected.
- Invalid empty tag values return `422 Unprocessable Entity`.

## Story 3
**As a** team member, **I want** to update the tags of an existing task **so that** I can keep its categories accurate when the work changes.

**Acceptance Criteria:**
- Tags can be added or removed through the Edit Task modal.
- Saving the edit updates the task through the existing PATCH behavior.
- The updated tags appear on the task card after the request succeeds.
- Other task fields remain unchanged when only tags are updated.

## Story 4
**As a** team member, **I want** tasks without tags to remain valid **so that** tags can stay optional when categorization is not needed.

**Acceptance Criteria:**
- A task can be created without tags.
- A task with no tags is successfully returned by the API.
- The task card does not show empty tag chips or placeholder tag values.
- Existing create and edit behavior continues to work without tags.

## Story 5
**As a** team member, **I want** to filter tasks by tag **so that** I can quickly find tasks belonging to a specific category.

**Acceptance Criteria:**
- A tag filter is available in the frontend.
- Selecting a tag displays only tasks containing that tag.
- A filter with no matching tasks displays the existing empty states.
- Clearing the filter restores all tasks.
- Filtering does not change or delete task data.

# User Stories — Feature 2: Task Comments

## Story 1
**As a** team member, **I want** to add a comment to a task **so that** I can record notes or context about the work as it progresses.

**Acceptance Criteria:**
- A comment requires non-blank text; whitespace-only or empty text returns 422.
- A comment is associated with a specific task and includes a timestamp.
- Adding a comment to a non-existent task returns 404.
- The new comment appears immediately after being added.

## Story 2
**As a** team member, **I want** to view all comments on a task **so that** I can see its full discussion history.

**Acceptance Criteria:**
- Comments are listed in the order they were added.
- A task with no comments returns an empty list, not an error.
- Requesting comments for a non-existent task returns 404.

## Story 3
**As a** team member, **I want** to delete a comment I added by mistake **so that** the task's comment history stays accurate.

**Acceptance Criteria:**
- Deleting a comment removes only that comment; other comments on the task are unaffected.
- Deleting a comment on a non-existent task returns 404.
- Deleting a non-existent comment ID returns 404.

## Story 5
**As a** team member, **I want** to see a comment count on each task card **so that** I can tell which tasks have active discussion without opening them.

**Acceptance Criteria:**
- Each task card shows the current number of comments.
- The count updates after a comment is added or deleted.
- Tasks with zero comments show no misleading placeholder.
