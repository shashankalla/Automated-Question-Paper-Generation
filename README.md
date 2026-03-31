# Automated Question Paper Generation System

A full-stack web application for generating balanced exam question papers based on **Bloom's Taxonomy** and **Course Outcome (CO) mapping**. Designed for teachers and educators to rapidly create well-structured question papers with minimal effort.

---

## Features

- **Question Paper Generation** – Select subject, units, difficulty distribution, and CO mapping to generate a unique paper
- **Bloom's Taxonomy Alignment** – Each question is tagged with a Bloom's level (Remember through Create)
- **CO Mapping** – Every question is mapped to a Course Outcome (CO1-CO6)
- **No Duplicate Questions** – Ensures each generated paper contains unique questions
- **Balanced Difficulty** – Configurable Easy / Medium / Hard split
- **PDF Export** – Download the generated paper as a formatted PDF
- **Admin Panel** – Add, edit, delete, and filter questions via a clean UI
- **Sample Dataset** – 50+ sample questions across 6 subjects to get started quickly

---

## Tech Stack

| Layer     | Technology                      |
|-----------|---------------------------------|
| Frontend  | HTML5, CSS3, Vanilla JavaScript |
| Backend   | Python 3.9+, Flask 3.x          |
| Database  | SQLite (via Flask-SQLAlchemy)   |
| PDF       | ReportLab                       |

---

## Project Structure

```
Automated-Question-Paper-Generation/
├── app.py              # Flask application (routes, models, PDF generation)
├── sample_data.py      # Script to load sample questions into the database
├── requirements.txt    # Python dependencies
├── templates/
│   ├── base.html       # Base layout template
│   ├── index.html      # Question paper generation form
│   ├── result.html     # Generated paper view
│   └── admin/
│       ├── dashboard.html    # Admin statistics dashboard
│       ├── questions.html    # Question list with filters
│       └── add_question.html # Add / edit question form
├── static/
│   ├── css/style.css   # Application stylesheet
│   └── js/main.js      # Frontend JavaScript
└── tests/
    └── test_app.py     # Pytest test suite
```

---

## Setup Instructions

### Prerequisites

- Python 3.9 or higher
- pip

### 1. Clone the repository

```bash
git clone https://github.com/shashankalla/Automated-Question-Paper-Generation.git
cd Automated-Question-Paper-Generation
```

### 2. Create and activate a virtual environment (recommended)

```bash
python -m venv venv
# Linux / macOS
source venv/bin/activate
# Windows
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Load the sample dataset

```bash
python sample_data.py
```

This populates the SQLite database (`instance/questions.db`) with 50+ sample questions across subjects such as Computer Science, Data Structures, Database Management Systems, Operating Systems, Software Engineering, and Mathematics.

### 5. Run the application

```bash
python app.py
```

Open your browser and navigate to **http://127.0.0.1:5000**

---

## Usage

### Generate a Question Paper

1. Go to the **Generate Paper** page (home).
2. Select a **Subject** and one or more **Units**.
3. Set the **Number of Questions** and the **Difficulty Distribution** (Easy / Medium / Hard counts).
4. Optionally select specific **Course Outcomes (COs)** to include.
5. Click **Generate Question Paper**.
6. View the paper and click **Download PDF** to export it.

### Admin Panel

Navigate to **/admin** to:
- View question statistics by subject and difficulty
- Add new questions (with subject, unit, difficulty, Bloom's level, CO mapping, marks)
- Edit or delete existing questions
- Filter questions by subject, unit, or difficulty

---

## Running Tests

```bash
pip install pytest
pytest tests/ -v
```

---

## Question Fields

| Field           | Description                                      |
|-----------------|--------------------------------------------------|
| `question_text` | The full text of the question                    |
| `subject`       | Subject name (e.g., Computer Science)            |
| `unit`          | Unit number (Unit 1 - Unit 5)                    |
| `difficulty`    | Easy, Medium, or Hard                            |
| `blooms_level`  | Bloom's taxonomy level (Remember through Create) |
| `co_mapping`    | Course Outcome (CO1 - CO6)                       |
| `marks`         | Marks allotted (2, 5, or 10)                     |

---

## Sample Dataset

The `sample_data.py` script loads questions for:
- **Computer Science** (10 questions)
- **Data Structures** (10 questions)
- **Database Management Systems** (10 questions)
- **Operating Systems** (8 questions)
- **Software Engineering** (7 questions)
- **Mathematics** (6 questions)
