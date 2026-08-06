# FILE: app/business_rules.py

from fastapi import HTTPException, status

from app.models import TaskStatus


VALID_TRANSITIONS: frozenset[tuple[TaskStatus, TaskStatus]] = frozenset(
    {
        (TaskStatus.TODO, TaskStatus.IN_PROGRESS),
        (TaskStatus.IN_PROGRESS, TaskStatus.DONE),
        (TaskStatus.DONE, TaskStatus.IN_PROGRESS),
        (TaskStatus.TODO, TaskStatus.TODO),
        (TaskStatus.IN_PROGRESS, TaskStatus.IN_PROGRESS),
        (TaskStatus.DONE, TaskStatus.DONE),
        #(TaskStatus.IN_PROGRESS, TaskStatus.TODO),
    }
)


def validate_status_transition(
    current: TaskStatus,
    new: TaskStatus,
) -> None:
    """Validate that a task status transition is allowed.

    Args:
        current (TaskStatus): The task's current status.
        new (TaskStatus): The requested new status.

    Returns:
        None: Returns nothing when the transition is valid.

    Raises:
        HTTPException: 422 Unprocessable Entity if `(current, new)` is
            not one of the allowed transitions in `VALID_TRANSITIONS`.
    """
    if (current, new) not in VALID_TRANSITIONS:
        allowed = sorted(
            {
                f"{from_status.value}->{to_status.value}"
                for from_status, to_status in VALID_TRANSITIONS
            }
        )

        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                f"Invalid status transition from {current.value} to "
                f"{new.value}. Allowed transitions: {allowed}"
            ),
        )