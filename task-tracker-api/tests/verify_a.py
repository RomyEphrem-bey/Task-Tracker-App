# tests/verify_a.py  -  Part A verifications. Run: python -m tests.verify_a

from pydantic import ValidationError
from app.models import TaskCreate, TaskUpdate, TaskStatus, TaskPriority


def expect_fail(label, fn):
    try:
        fn()
        print(f"FAIL: {label} - accepted but should have been rejected")
    except ValidationError:
        print(f"PASS: {label}")


def expect_ok(label, fn):
    try:
        fn()
        print(f"PASS: {label}")
    except Exception as e:
        print(f"FAIL: {label} - {e}")


# 1. Whitespace title rejected
expect_fail("whitespace title rejected", lambda: TaskCreate(title=" "))

# 2. Empty title rejected
expect_fail("empty title rejected", lambda: TaskCreate(title=""))

# 3. Title over 200 chars rejected
expect_fail("title over 200 chars rejected", lambda: TaskCreate(title="x" * 201))

# 4. Valid title accepted, defaults applied
def _ok_defaults():
    t = TaskCreate(title="Hello")
    assert t.status == TaskStatus.TODO
    assert t.priority == TaskPriority.MEDIUM
    assert t.description == ""
    assert t.assignee is None


expect_ok("defaults applied (ToDo, Medium, empty description)", _ok_defaults)

# 5. extra='forbid' - unknown field rejected on TaskCreate
expect_fail("extra field rejected on TaskCreate", lambda: TaskCreate(title="x", unknown="y"))

# 6. id NOT settable via TaskCreate
expect_fail("id rejected on TaskCreate", lambda: TaskCreate(title="x", id="123"))

# 7. created_at NOT settable via TaskUpdate
expect_fail("created_at rejected on TaskUpdate", lambda: TaskUpdate(created_at="2024-01-01"))

# 8. Invalid enum value rejected
expect_fail("invalid status rejected", lambda: TaskCreate(title="x", status="BadStatus"))

print("--- Part A verifications complete ---")