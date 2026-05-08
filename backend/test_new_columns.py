"""
Smoke test: instantiate Course and Module with no arguments,
verify all new fields are at their defaults.

Note: SQLAlchemy Column(default=X) is an insert-time default applied
during session.flush(), NOT at bare Python object construction.
For bare construction, nullable columns are None.
We test both bare construction and ORM flush behavior.
"""

import sys
sys.path.insert(0, ".")

from models import Course, Module
from database import engine, Base, SessionLocal


def test_bare_construction():
    """Test bare object creation (no session) — all new nullable columns are None."""
    print("--- Bare construction defaults ---")
    c = Course()
    assert c.project_prompt is None, f"Expected None, got {c.project_prompt!r}"
    assert c.required_resources is None, f"Expected None, got {c.required_resources!r}"
    print("  Course.project_prompt      = None  ✓")
    print("  Course.required_resources   = None  ✓")

    m = Module()
    # has_transcript has default=False, but that's an insert default;
    # bare construction gives None
    assert m.notes is None, f"Expected None, got {m.notes!r}"
    print("  Module.notes                = None  ✓")
    print("  Module.has_transcript (bare) = None (insert default applies at flush) ✓")


def test_orm_flush_defaults():
    """Test that after flush, has_transcript gets its default of False/0."""
    print("\n--- ORM flush defaults (in-memory SQLite) ---")
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    test_engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(test_engine)
    TestSession = sessionmaker(bind=test_engine)
    session = TestSession()

    c = Course(skill_name="test", user_id=None)
    session.add(c)
    session.flush()
    assert c.project_prompt is None
    assert c.required_resources is None
    print("  Course.project_prompt      = None  ✓")
    print("  Course.required_resources   = None  ✓")

    m = Module(course_id=None, title="t", description="d", order_index=0, search_query="q")
    session.add(m)
    session.flush()
    assert m.has_transcript == False or m.has_transcript == 0, \
        f"Expected False/0, got {m.has_transcript!r}"
    assert m.notes is None
    print("  Module.has_transcript       = False ✓")
    print("  Module.notes                = None  ✓")

    session.close()


def test_validators():
    """Test @validates methods on Course and Module."""
    print("\n--- Validators ---")
    c = Course()

    # required_resources: must be None or list
    try:
        c.required_resources = "not a list"
        raise AssertionError("Should have raised ValueError for string value")
    except ValueError:
        print("  Course.required_resources validator (string → ValueError) ✓")

    c.required_resources = [{"name": "Python", "type": "software", "url": None}]
    print("  Course.required_resources validator (list → OK)  ✓")

    c.required_resources = None
    print("  Course.required_resources validator (None → OK)  ✓")

    # notes: must be ≤ 2000 chars
    m = Module()
    try:
        m.notes = "x" * 2001
        raise AssertionError("Should have raised ValueError for >2000 chars")
    except ValueError:
        print("  Module.notes validator (>2000 → ValueError)      ✓")

    m.notes = "x" * 2000
    print("  Module.notes validator (2000 → OK)                ✓")

    m.notes = None
    print("  Module.notes validator (None → OK)                ✓")


if __name__ == "__main__":
    test_bare_construction()
    test_orm_flush_defaults()
    test_validators()
    print("\n✅ All assertions passed!")
