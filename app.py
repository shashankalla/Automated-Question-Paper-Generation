"""
Automated Question Paper Generation System
Flask backend application with SQLite database.
"""

import io
import random
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    send_file,
    jsonify,
)
from flask_sqlalchemy import SQLAlchemy
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT

# ---------------------------------------------------------------------------
# Application setup
# ---------------------------------------------------------------------------

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///questions.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "qpgen-secret-key-change-in-production"

db = SQLAlchemy(app)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SUBJECTS = [
    "Mathematics",
    "Physics",
    "Chemistry",
    "Computer Science",
    "Data Structures",
    "Database Management Systems",
    "Operating Systems",
    "Software Engineering",
]

UNITS = ["Unit 1", "Unit 2", "Unit 3", "Unit 4", "Unit 5"]

DIFFICULTY_LEVELS = ["Easy", "Medium", "Hard"]

BLOOMS_LEVELS = [
    "Remember",
    "Understand",
    "Apply",
    "Analyze",
    "Evaluate",
    "Create",
]

CO_LIST = ["CO1", "CO2", "CO3", "CO4", "CO5", "CO6"]

MARKS_OPTIONS = [2, 5, 10]

# ---------------------------------------------------------------------------
# Database model
# ---------------------------------------------------------------------------


class Question(db.Model):
    """Represents a single question stored in the database."""

    __tablename__ = "questions"

    id = db.Column(db.Integer, primary_key=True)
    # Question content
    question_text = db.Column(db.Text, nullable=False)
    subject = db.Column(db.String(100), nullable=False)
    unit = db.Column(db.String(50), nullable=False)
    # Classification
    difficulty = db.Column(db.String(20), nullable=False)
    blooms_level = db.Column(db.String(50), nullable=False)
    co_mapping = db.Column(db.String(20), nullable=False)
    marks = db.Column(db.Integer, nullable=False, default=2)

    def __repr__(self):
        return f"<Question id={self.id} subject={self.subject} unit={self.unit}>"

    def to_dict(self):
        """Return a plain dictionary representation of the question."""
        return {
            "id": self.id,
            "question_text": self.question_text,
            "subject": self.subject,
            "unit": self.unit,
            "difficulty": self.difficulty,
            "blooms_level": self.blooms_level,
            "co_mapping": self.co_mapping,
            "marks": self.marks,
        }


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def generate_paper(subject, units, num_questions, difficulty_dist, co_dist):
    """
    Select questions from the database according to the given criteria.

    Parameters
    ----------
    subject : str
    units : list[str]
    num_questions : int
    difficulty_dist : dict  {"Easy": n, "Medium": n, "Hard": n}
    co_dist : dict          {"CO1": n, ...}  (values are relative weights, not strict counts)

    Returns
    -------
    list[Question]  The selected questions (no duplicates).
    str             An error message, or empty string on success.
    """
    selected = []
    used_ids = set()

    # --- difficulty-based selection ---
    for diff, count in difficulty_dist.items():
        if count <= 0:
            continue
        candidates = Question.query.filter(
            Question.subject == subject,
            Question.unit.in_(units),
            Question.difficulty == diff,
        ).all()
        random.shuffle(candidates)
        for q in candidates:
            if len(selected) >= num_questions:
                break
            if q.id not in used_ids and count > 0:
                selected.append(q)
                used_ids.add(q.id)
                count -= 1

    # --- fill remaining slots with any available question ---
    if len(selected) < num_questions:
        remaining = Question.query.filter(
            Question.subject == subject,
            Question.unit.in_(units),
            ~Question.id.in_(used_ids) if used_ids else True,
        ).all()
        random.shuffle(remaining)
        for q in remaining:
            if len(selected) >= num_questions:
                break
            if q.id not in used_ids:
                selected.append(q)
                used_ids.add(q.id)

    if not selected:
        return [], "No questions found for the selected criteria."

    if len(selected) < num_questions:
        return selected, (
            f"Only {len(selected)} question(s) available for the selected criteria "
            f"(requested {num_questions})."
        )

    return selected, ""


def build_pdf(paper_title, subject, questions):
    """
    Generate a PDF question paper in memory and return a BytesIO object.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "Title",
        parent=styles["Heading1"],
        alignment=TA_CENTER,
        fontSize=16,
        spaceAfter=6,
    )
    sub_style = ParagraphStyle(
        "Sub",
        parent=styles["Normal"],
        alignment=TA_CENTER,
        fontSize=12,
        spaceAfter=4,
    )
    header_style = ParagraphStyle(
        "Header",
        parent=styles["Normal"],
        alignment=TA_CENTER,
        fontSize=10,
        spaceAfter=12,
    )
    question_style = ParagraphStyle(
        "Question",
        parent=styles["Normal"],
        fontSize=11,
        leading=16,
        spaceBefore=4,
        spaceAfter=4,
    )
    meta_style = ParagraphStyle(
        "Meta",
        parent=styles["Normal"],
        fontSize=9,
        textColor=colors.grey,
        spaceAfter=8,
    )

    story = []

    # Header
    story.append(Paragraph("AUTOMATED QUESTION PAPER", title_style))
    story.append(Paragraph(paper_title, sub_style))
    story.append(Paragraph(f"Subject: {subject}", header_style))
    story.append(Spacer(1, 0.3 * cm))

    # Divider line via a thin table
    divider_data = [[""]]
    divider_table = Table(divider_data, colWidths=[17 * cm])
    divider_table.setStyle(
        TableStyle(
            [
                ("LINEBELOW", (0, 0), (-1, 0), 1, colors.black),
                ("TOPPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    story.append(divider_table)
    story.append(Spacer(1, 0.3 * cm))

    total_marks = sum(q.marks for q in questions)
    story.append(
        Paragraph(
            f"Total Questions: {len(questions)}  |  Total Marks: {total_marks}",
            header_style,
        )
    )
    story.append(Spacer(1, 0.5 * cm))

    # Questions
    for idx, q in enumerate(questions, start=1):
        story.append(
            Paragraph(
                f"<b>Q{idx}.</b> {q.question_text} <b>[{q.marks} marks]</b>",
                question_style,
            )
        )
        story.append(
            Paragraph(
                f"Unit: {q.unit}  |  Difficulty: {q.difficulty}  "
                f"|  CO: {q.co_mapping}  |  Bloom's: {q.blooms_level}",
                meta_style,
            )
        )

    doc.build(story)
    buffer.seek(0)
    return buffer


# ---------------------------------------------------------------------------
# Routes – Main (question paper generation)
# ---------------------------------------------------------------------------


@app.route("/")
def index():
    """Landing page – question paper generation form."""
    return render_template(
        "index.html",
        subjects=SUBJECTS,
        units=UNITS,
        difficulty_levels=DIFFICULTY_LEVELS,
        blooms_levels=BLOOMS_LEVELS,
        co_list=CO_LIST,
    )


@app.route("/generate", methods=["POST"])
def generate():
    """Process the generation form and display the resulting paper."""
    subject = request.form.get("subject", "").strip()
    units = request.form.getlist("units")
    num_questions = request.form.get("num_questions", "10")
    co_values = request.form.getlist("co_mapping")

    # Difficulty distribution
    easy_count = int(request.form.get("easy_count", 0))
    medium_count = int(request.form.get("medium_count", 0))
    hard_count = int(request.form.get("hard_count", 0))

    # Validation
    errors = []
    if not subject:
        errors.append("Please select a subject.")
    if not units:
        errors.append("Please select at least one unit.")

    try:
        num_questions = int(num_questions)
        if num_questions < 1:
            raise ValueError
    except ValueError:
        errors.append("Number of questions must be a positive integer.")
        num_questions = 10

    if errors:
        for e in errors:
            flash(e, "danger")
        return redirect(url_for("index"))

    difficulty_dist = {
        "Easy": easy_count,
        "Medium": medium_count,
        "Hard": hard_count,
    }

    # If no difficulty distribution given, split evenly
    if easy_count + medium_count + hard_count == 0:
        each = num_questions // 3
        remainder = num_questions % 3
        difficulty_dist = {
            "Easy": each + (1 if remainder > 0 else 0),
            "Medium": each + (1 if remainder > 1 else 0),
            "Hard": each,
        }

    co_dist = {co: 1 for co in co_values} if co_values else {}

    paper_title = request.form.get("paper_title", "End Semester Examination").strip()

    questions, warning = generate_paper(
        subject, units, num_questions, difficulty_dist, co_dist
    )

    if warning:
        flash(warning, "warning")

    if not questions:
        flash("No questions could be generated. Please add questions to the database first.", "danger")
        return redirect(url_for("index"))

    total_marks = sum(q.marks for q in questions)

    return render_template(
        "result.html",
        questions=questions,
        subject=subject,
        units=units,
        paper_title=paper_title,
        total_marks=total_marks,
    )


@app.route("/download-pdf", methods=["POST"])
def download_pdf():
    """Generate and send a PDF of the question paper."""
    subject = request.form.get("subject", "Unknown Subject")
    paper_title = request.form.get("paper_title", "Question Paper")

    # Reconstruct question list from form
    question_ids_raw = request.form.get("question_ids", "")
    if not question_ids_raw:
        flash("No questions to export.", "danger")
        return redirect(url_for("index"))

    try:
        question_ids = [int(x) for x in question_ids_raw.split(",") if x.strip()]
    except ValueError:
        flash("Invalid question data for PDF export.", "danger")
        return redirect(url_for("index"))

    questions = Question.query.filter(Question.id.in_(question_ids)).all()
    # Preserve order
    id_to_q = {q.id: q for q in questions}
    ordered_questions = [id_to_q[qid] for qid in question_ids if qid in id_to_q]

    pdf_buffer = build_pdf(paper_title, subject, ordered_questions)

    filename = f"{subject.replace(' ', '_')}_Question_Paper.pdf"
    return send_file(
        pdf_buffer,
        mimetype="application/pdf",
        as_attachment=True,
        download_name=filename,
    )


# ---------------------------------------------------------------------------
# Routes – Admin panel
# ---------------------------------------------------------------------------


@app.route("/admin")
def admin_dashboard():
    """Admin dashboard showing question statistics."""
    total_questions = Question.query.count()

    subject_counts = {}
    for subj in SUBJECTS:
        count = Question.query.filter_by(subject=subj).count()
        if count > 0:
            subject_counts[subj] = count

    difficulty_counts = {
        diff: Question.query.filter_by(difficulty=diff).count()
        for diff in DIFFICULTY_LEVELS
    }

    return render_template(
        "admin/dashboard.html",
        total_questions=total_questions,
        subject_counts=subject_counts,
        difficulty_counts=difficulty_counts,
        subjects=SUBJECTS,
    )


@app.route("/admin/questions")
def admin_questions():
    """List all questions with optional filters."""
    subject_filter = request.args.get("subject", "")
    unit_filter = request.args.get("unit", "")
    difficulty_filter = request.args.get("difficulty", "")

    query = Question.query
    if subject_filter:
        query = query.filter_by(subject=subject_filter)
    if unit_filter:
        query = query.filter_by(unit=unit_filter)
    if difficulty_filter:
        query = query.filter_by(difficulty=difficulty_filter)

    questions = query.order_by(Question.subject, Question.unit, Question.id).all()

    return render_template(
        "admin/questions.html",
        questions=questions,
        subjects=SUBJECTS,
        units=UNITS,
        difficulty_levels=DIFFICULTY_LEVELS,
        subject_filter=subject_filter,
        unit_filter=unit_filter,
        difficulty_filter=difficulty_filter,
    )


@app.route("/admin/questions/add", methods=["GET", "POST"])
def admin_add_question():
    """Add a new question."""
    if request.method == "POST":
        question_text = request.form.get("question_text", "").strip()
        subject = request.form.get("subject", "").strip()
        unit = request.form.get("unit", "").strip()
        difficulty = request.form.get("difficulty", "").strip()
        blooms_level = request.form.get("blooms_level", "").strip()
        co_mapping = request.form.get("co_mapping", "").strip()
        marks = request.form.get("marks", "2")

        errors = []
        if not question_text:
            errors.append("Question text is required.")
        if subject not in SUBJECTS:
            errors.append("Invalid subject.")
        if unit not in UNITS:
            errors.append("Invalid unit.")
        if difficulty not in DIFFICULTY_LEVELS:
            errors.append("Invalid difficulty level.")
        if blooms_level not in BLOOMS_LEVELS:
            errors.append("Invalid Bloom's level.")
        if co_mapping not in CO_LIST:
            errors.append("Invalid CO mapping.")
        try:
            marks = int(marks)
            if marks not in MARKS_OPTIONS:
                raise ValueError
        except ValueError:
            errors.append("Marks must be one of: 2, 5, 10.")

        if errors:
            for e in errors:
                flash(e, "danger")
            return render_template(
                "admin/add_question.html",
                subjects=SUBJECTS,
                units=UNITS,
                difficulty_levels=DIFFICULTY_LEVELS,
                blooms_levels=BLOOMS_LEVELS,
                co_list=CO_LIST,
                marks_options=MARKS_OPTIONS,
                form_data=request.form,
                edit_mode=False,
            )

        q = Question(
            question_text=question_text,
            subject=subject,
            unit=unit,
            difficulty=difficulty,
            blooms_level=blooms_level,
            co_mapping=co_mapping,
            marks=marks,
        )
        db.session.add(q)
        db.session.commit()
        flash("Question added successfully!", "success")
        return redirect(url_for("admin_questions"))

    return render_template(
        "admin/add_question.html",
        subjects=SUBJECTS,
        units=UNITS,
        difficulty_levels=DIFFICULTY_LEVELS,
        blooms_levels=BLOOMS_LEVELS,
        co_list=CO_LIST,
        marks_options=MARKS_OPTIONS,
        form_data={},
        edit_mode=False,
    )


@app.route("/admin/questions/edit/<int:question_id>", methods=["GET", "POST"])
def admin_edit_question(question_id):
    """Edit an existing question."""
    q = Question.query.get_or_404(question_id)

    if request.method == "POST":
        question_text = request.form.get("question_text", "").strip()
        subject = request.form.get("subject", "").strip()
        unit = request.form.get("unit", "").strip()
        difficulty = request.form.get("difficulty", "").strip()
        blooms_level = request.form.get("blooms_level", "").strip()
        co_mapping = request.form.get("co_mapping", "").strip()
        marks = request.form.get("marks", "2")

        errors = []
        if not question_text:
            errors.append("Question text is required.")
        if subject not in SUBJECTS:
            errors.append("Invalid subject.")
        if unit not in UNITS:
            errors.append("Invalid unit.")
        if difficulty not in DIFFICULTY_LEVELS:
            errors.append("Invalid difficulty level.")
        if blooms_level not in BLOOMS_LEVELS:
            errors.append("Invalid Bloom's level.")
        if co_mapping not in CO_LIST:
            errors.append("Invalid CO mapping.")
        try:
            marks = int(marks)
            if marks not in MARKS_OPTIONS:
                raise ValueError
        except ValueError:
            errors.append("Marks must be one of: 2, 5, 10.")

        if errors:
            for e in errors:
                flash(e, "danger")
            return render_template(
                "admin/add_question.html",
                subjects=SUBJECTS,
                units=UNITS,
                difficulty_levels=DIFFICULTY_LEVELS,
                blooms_levels=BLOOMS_LEVELS,
                co_list=CO_LIST,
                marks_options=MARKS_OPTIONS,
                form_data=request.form,
                edit_mode=True,
                question_id=question_id,
            )

        q.question_text = question_text
        q.subject = subject
        q.unit = unit
        q.difficulty = difficulty
        q.blooms_level = blooms_level
        q.co_mapping = co_mapping
        q.marks = marks
        db.session.commit()
        flash("Question updated successfully!", "success")
        return redirect(url_for("admin_questions"))

    return render_template(
        "admin/add_question.html",
        subjects=SUBJECTS,
        units=UNITS,
        difficulty_levels=DIFFICULTY_LEVELS,
        blooms_levels=BLOOMS_LEVELS,
        co_list=CO_LIST,
        marks_options=MARKS_OPTIONS,
        form_data=q.to_dict(),
        edit_mode=True,
        question_id=question_id,
    )


@app.route("/admin/questions/delete/<int:question_id>", methods=["POST"])
def admin_delete_question(question_id):
    """Delete a question."""
    q = Question.query.get_or_404(question_id)
    db.session.delete(q)
    db.session.commit()
    flash("Question deleted successfully.", "success")
    return redirect(url_for("admin_questions"))


# ---------------------------------------------------------------------------
# API endpoints (JSON) for dynamic frontend interactions
# ---------------------------------------------------------------------------


@app.route("/api/questions/count")
def api_question_count():
    """Return question count for a given subject/unit combination."""
    subject = request.args.get("subject", "")
    units = request.args.getlist("units")

    if not subject or not units:
        return jsonify({"count": 0})

    count = Question.query.filter(
        Question.subject == subject,
        Question.unit.in_(units),
    ).count()
    return jsonify({"count": count})


# ---------------------------------------------------------------------------
# Application entry point
# ---------------------------------------------------------------------------


def init_db():
    """Create database tables."""
    with app.app_context():
        db.create_all()


if __name__ == "__main__":
    import os

    init_db()
    debug_mode = os.environ.get("FLASK_DEBUG", "0") == "1"
    app.run(debug=debug_mode, port=5000)
