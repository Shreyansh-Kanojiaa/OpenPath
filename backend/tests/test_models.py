import pytest

from models import Course, Module


def test_bare_construction_defaults():
    """Bare object creation (no session): nullable columns are None until flush."""
    c = Course()
    assert c.project_prompt is None
    assert c.required_resources is None

    m = Module()
    assert m.notes is None


def test_orm_flush_defaults(db_engine):
    from sqlalchemy.orm import sessionmaker

    Session = sessionmaker(bind=db_engine)
    session = Session()

    c = Course(skill_name="test", user_id=None)
    session.add(c)
    session.flush()
    assert c.project_prompt is None
    assert c.required_resources is None

    m = Module(course_id=None, title="t", description="d", order_index=0, search_query="q")
    session.add(m)
    session.flush()
    assert m.has_transcript in (False, 0)
    assert m.notes is None

    session.close()


def test_course_required_resources_validator():
    c = Course()
    with pytest.raises(ValueError):
        c.required_resources = "not a list"

    c.required_resources = [{"name": "Python", "type": "software", "url": None}]
    assert c.required_resources == [{"name": "Python", "type": "software", "url": None}]

    c.required_resources = None
    assert c.required_resources is None


def test_module_notes_validator():
    m = Module()
    with pytest.raises(ValueError):
        m.notes = "x" * 2001

    m.notes = "x" * 2000
    assert len(m.notes) == 2000

    m.notes = None
    assert m.notes is None
