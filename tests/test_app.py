"""
Tests for the Automated Question Paper Generation System.
"""

import json
import os
import sys
import pytest

# Ensure the project root is on the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app as flask_app, db, Question, generate_paper


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def app():
    """Configure the Flask application for testing with an in-memory DB."""
    flask_app.config["TESTING"] = True
    flask_app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    flask_app.config["WTF_CSRF_ENABLED"] = False
    flask_app.config["SECRET_KEY"] = "test-secret"

    with flask_app.app_context():
        db.create_all()
        _seed_test_data()
        yield flask_app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


def _seed_test_data():
    """Insert a small set of questions covering all difficulty levels."""
    questions = [
        Question(
            question_text="Define an algorithm.",
            subject="Computer Science",
            unit="Unit 1",
            difficulty="Easy",
            blooms_level="Remember",
            co_mapping="CO1",
            marks=2,
        ),
        Question(
            question_text="Explain time complexity.",
            subject="Computer Science",
            unit="Unit 1",
            difficulty="Medium",
            blooms_level="Understand",
            co_mapping="CO1",
            marks=5,
        ),
        Question(
            question_text="Analyze bubble sort.",
            subject="Computer Science",
            unit="Unit 2",
            difficulty="Hard",
            blooms_level="Analyze",
            co_mapping="CO2",
            marks=10,
        ),
        Question(
            question_text="What is a stack?",
            subject="Data Structures",
            unit="Unit 1",
            difficulty="Easy",
            blooms_level="Remember",
            co_mapping="CO1",
            marks=2,
        ),
        Question(
            question_text="Implement circular queue.",
            subject="Data Structures",
            unit="Unit 2",
            difficulty="Medium",
            blooms_level="Apply",
            co_mapping="CO2",
            marks=5,
        ),
        Question(
            question_text="Design an LRU cache.",
            subject="Data Structures",
            unit="Unit 3",
            difficulty="Hard",
            blooms_level="Create",
            co_mapping="CO3",
            marks=10,
        ),
        Question(
            question_text="Define DBMS.",
            subject="Database Management Systems",
            unit="Unit 1",
            difficulty="Easy",
            blooms_level="Remember",
            co_mapping="CO1",
            marks=2,
        ),
        Question(
            question_text="Explain three-schema architecture.",
            subject="Database Management Systems",
            unit="Unit 1",
            difficulty="Medium",
            blooms_level="Understand",
            co_mapping="CO1",
            marks=5,
        ),
        Question(
            question_text="Design a relational schema for e-commerce.",
            subject="Database Management Systems",
            unit="Unit 5",
            difficulty="Hard",
            blooms_level="Create",
            co_mapping="CO5",
            marks=10,
        ),
    ]
    db.session.bulk_save_objects(questions)
    db.session.commit()


# ---------------------------------------------------------------------------
# Model tests
# ---------------------------------------------------------------------------


class TestQuestionModel:
    def test_question_creation(self, app):
        with app.app_context():
            q = Question(
                question_text="Test question?",
                subject="Computer Science",
                unit="Unit 1",
                difficulty="Easy",
                blooms_level="Remember",
                co_mapping="CO1",
                marks=2,
            )
            db.session.add(q)
            db.session.commit()
            assert q.id is not None
            assert q.question_text == "Test question?"

    def test_to_dict(self, app):
        with app.app_context():
            q = Question.query.filter_by(subject="Computer Science").first()
            d = q.to_dict()
            assert "id" in d
            assert "question_text" in d
            assert "subject" in d
            assert "unit" in d
            assert "difficulty" in d
            assert "blooms_level" in d
            assert "co_mapping" in d
            assert "marks" in d

    def test_question_repr(self, app):
        with app.app_context():
            q = Question.query.first()
            assert "Question" in repr(q)


# ---------------------------------------------------------------------------
# Route tests – main
# ---------------------------------------------------------------------------


class TestIndexRoute:
    def test_index_get(self, client):
        response = client.get("/")
        assert response.status_code == 200
        assert b"Question Paper Generator" in response.data or b"Generate" in response.data

    def test_index_has_subjects(self, client):
        response = client.get("/")
        assert b"Computer Science" in response.data

    def test_index_has_units(self, client):
        response = client.get("/")
        assert b"Unit 1" in response.data


class TestGenerateRoute:
    def test_generate_success(self, client):
        response = client.post(
            "/generate",
            data={
                "subject": "Computer Science",
                "units": ["Unit 1", "Unit 2"],
                "num_questions": "2",
                "easy_count": "1",
                "medium_count": "1",
                "hard_count": "0",
                "paper_title": "Test Paper",
            },
            follow_redirects=True,
        )
        assert response.status_code == 200

    def test_generate_no_subject(self, client):
        response = client.post(
            "/generate",
            data={
                "subject": "",
                "units": ["Unit 1"],
                "num_questions": "5",
            },
            follow_redirects=True,
        )
        # Should redirect back to index with a flash error
        assert response.status_code == 200
        assert b"subject" in response.data.lower() or b"select" in response.data.lower()

    def test_generate_no_units(self, client):
        response = client.post(
            "/generate",
            data={
                "subject": "Computer Science",
                "num_questions": "5",
            },
            follow_redirects=True,
        )
        assert response.status_code == 200

    def test_generate_wrong_subject(self, client):
        """Generating for a subject with no questions shows a warning."""
        response = client.post(
            "/generate",
            data={
                "subject": "Physics",
                "units": ["Unit 1"],
                "num_questions": "3",
            },
            follow_redirects=True,
        )
        assert response.status_code == 200


# ---------------------------------------------------------------------------
# Route tests – Admin
# ---------------------------------------------------------------------------


class TestAdminRoutes:
    def test_admin_dashboard(self, client):
        response = client.get("/admin")
        assert response.status_code == 200
        assert b"Admin" in response.data

    def test_admin_questions_list(self, client):
        response = client.get("/admin/questions")
        assert response.status_code == 200
        assert b"Computer Science" in response.data

    def test_admin_questions_filter_by_subject(self, client):
        response = client.get("/admin/questions?subject=Data+Structures")
        assert response.status_code == 200

    def test_admin_add_question_get(self, client):
        response = client.get("/admin/questions/add")
        assert response.status_code == 200
        assert b"Add" in response.data

    def test_admin_add_question_post_valid(self, client, app):
        response = client.post(
            "/admin/questions/add",
            data={
                "question_text": "What is recursion?",
                "subject": "Computer Science",
                "unit": "Unit 1",
                "difficulty": "Easy",
                "blooms_level": "Remember",
                "co_mapping": "CO1",
                "marks": "2",
            },
            follow_redirects=True,
        )
        assert response.status_code == 200
        # Verify question was actually saved
        with app.app_context():
            q = Question.query.filter_by(question_text="What is recursion?").first()
            assert q is not None

    def test_admin_add_question_post_missing_text(self, client):
        response = client.post(
            "/admin/questions/add",
            data={
                "question_text": "",
                "subject": "Computer Science",
                "unit": "Unit 1",
                "difficulty": "Easy",
                "blooms_level": "Remember",
                "co_mapping": "CO1",
                "marks": "2",
            },
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert b"required" in response.data.lower() or b"Question text" in response.data

    def test_admin_edit_question_get(self, client, app):
        with app.app_context():
            q = Question.query.first()
            qid = q.id
        response = client.get(f"/admin/questions/edit/{qid}")
        assert response.status_code == 200
        assert b"Edit" in response.data

    def test_admin_edit_question_post_valid(self, client, app):
        with app.app_context():
            q = Question.query.first()
            qid = q.id
        response = client.post(
            f"/admin/questions/edit/{qid}",
            data={
                "question_text": "Updated question text.",
                "subject": "Computer Science",
                "unit": "Unit 1",
                "difficulty": "Easy",
                "blooms_level": "Remember",
                "co_mapping": "CO1",
                "marks": "2",
            },
            follow_redirects=True,
        )
        assert response.status_code == 200
        with app.app_context():
            q = db.session.get(Question, qid)
            assert q.question_text == "Updated question text."

    def test_admin_delete_question(self, client, app):
        with app.app_context():
            q = Question.query.first()
            qid = q.id
        response = client.post(
            f"/admin/questions/delete/{qid}",
            follow_redirects=True,
        )
        assert response.status_code == 200
        with app.app_context():
            assert db.session.get(Question, qid) is None

    def test_admin_edit_not_found(self, client):
        response = client.get("/admin/questions/edit/99999")
        assert response.status_code == 404

    def test_admin_delete_not_found(self, client):
        response = client.post("/admin/questions/delete/99999")
        assert response.status_code == 404


# ---------------------------------------------------------------------------
# API tests
# ---------------------------------------------------------------------------


class TestApiRoutes:
    def test_api_question_count_valid(self, client):
        response = client.get(
            "/api/questions/count?subject=Computer+Science&units=Unit+1"
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert "count" in data
        assert data["count"] >= 0

    def test_api_question_count_no_params(self, client):
        response = client.get("/api/questions/count")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["count"] == 0


# ---------------------------------------------------------------------------
# generate_paper logic tests
# ---------------------------------------------------------------------------


class TestGeneratePaperLogic:
    def test_generates_correct_count(self, app):
        with app.app_context():
            questions, error = generate_paper(
                subject="Computer Science",
                units=["Unit 1", "Unit 2"],
                num_questions=2,
                difficulty_dist={"Easy": 1, "Medium": 1, "Hard": 0},
                co_dist={},
            )
            assert len(questions) == 2
            assert error == ""

    def test_no_duplicate_questions(self, app):
        with app.app_context():
            questions, _ = generate_paper(
                subject="Data Structures",
                units=["Unit 1", "Unit 2", "Unit 3"],
                num_questions=3,
                difficulty_dist={"Easy": 1, "Medium": 1, "Hard": 1},
                co_dist={},
            )
            ids = [q.id for q in questions]
            assert len(ids) == len(set(ids))

    def test_empty_result_for_unknown_subject(self, app):
        with app.app_context():
            questions, error = generate_paper(
                subject="UnknownSubject",
                units=["Unit 1"],
                num_questions=5,
                difficulty_dist={"Easy": 2, "Medium": 2, "Hard": 1},
                co_dist={},
            )
            assert questions == []
            assert error != ""

    def test_partial_result_warning(self, app):
        """Requesting more questions than available returns a warning."""
        with app.app_context():
            questions, error = generate_paper(
                subject="Computer Science",
                units=["Unit 1"],
                num_questions=100,
                difficulty_dist={"Easy": 50, "Medium": 50, "Hard": 0},
                co_dist={},
            )
            # Should return whatever is available and produce a warning
            assert len(questions) > 0
            assert len(questions) < 100
            assert error != ""

    def test_difficulty_distribution(self, app):
        with app.app_context():
            questions, _ = generate_paper(
                subject="Database Management Systems",
                units=["Unit 1", "Unit 5"],
                num_questions=3,
                difficulty_dist={"Easy": 1, "Medium": 1, "Hard": 1},
                co_dist={},
            )
            difficulties = {q.difficulty for q in questions}
            # All three difficulties should be represented
            assert "Easy" in difficulties
            assert "Medium" in difficulties
            assert "Hard" in difficulties
