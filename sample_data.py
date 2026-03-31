"""
Sample dataset loader for the Automated Question Paper Generation System.
Run this script once to populate the database with sample questions.

Usage:
    python sample_data.py
"""

from app import app, db, Question

# ---------------------------------------------------------------------------
# Sample questions grouped by subject
# ---------------------------------------------------------------------------

SAMPLE_QUESTIONS = [
    # -----------------------------------------------------------------------
    # Computer Science
    # -----------------------------------------------------------------------
    {
        "question_text": "Define an algorithm and list its essential characteristics.",
        "subject": "Computer Science",
        "unit": "Unit 1",
        "difficulty": "Easy",
        "blooms_level": "Remember",
        "co_mapping": "CO1",
        "marks": 2,
    },
    {
        "question_text": "Explain the concept of time complexity with an example.",
        "subject": "Computer Science",
        "unit": "Unit 1",
        "difficulty": "Medium",
        "blooms_level": "Understand",
        "co_mapping": "CO1",
        "marks": 5,
    },
    {
        "question_text": "Analyze the best, average, and worst case complexities of Bubble Sort.",
        "subject": "Computer Science",
        "unit": "Unit 2",
        "difficulty": "Hard",
        "blooms_level": "Analyze",
        "co_mapping": "CO2",
        "marks": 10,
    },
    {
        "question_text": "What is a flowchart? List its symbols.",
        "subject": "Computer Science",
        "unit": "Unit 1",
        "difficulty": "Easy",
        "blooms_level": "Remember",
        "co_mapping": "CO1",
        "marks": 2,
    },
    {
        "question_text": "Differentiate between compiler and interpreter.",
        "subject": "Computer Science",
        "unit": "Unit 1",
        "difficulty": "Easy",
        "blooms_level": "Understand",
        "co_mapping": "CO1",
        "marks": 2,
    },
    {
        "question_text": "Implement binary search and analyze its time complexity.",
        "subject": "Computer Science",
        "unit": "Unit 2",
        "difficulty": "Medium",
        "blooms_level": "Apply",
        "co_mapping": "CO2",
        "marks": 5,
    },
    {
        "question_text": "Design an algorithm to detect a cycle in a directed graph.",
        "subject": "Computer Science",
        "unit": "Unit 3",
        "difficulty": "Hard",
        "blooms_level": "Create",
        "co_mapping": "CO3",
        "marks": 10,
    },
    {
        "question_text": "Explain the principles of Object-Oriented Programming.",
        "subject": "Computer Science",
        "unit": "Unit 3",
        "difficulty": "Easy",
        "blooms_level": "Understand",
        "co_mapping": "CO3",
        "marks": 2,
    },
    {
        "question_text": "Compare and contrast procedural and OOP paradigms.",
        "subject": "Computer Science",
        "unit": "Unit 3",
        "difficulty": "Medium",
        "blooms_level": "Analyze",
        "co_mapping": "CO3",
        "marks": 5,
    },
    {
        "question_text": "Design a class hierarchy for a library management system.",
        "subject": "Computer Science",
        "unit": "Unit 4",
        "difficulty": "Hard",
        "blooms_level": "Create",
        "co_mapping": "CO4",
        "marks": 10,
    },
    # -----------------------------------------------------------------------
    # Data Structures
    # -----------------------------------------------------------------------
    {
        "question_text": "Define a stack and mention its operations.",
        "subject": "Data Structures",
        "unit": "Unit 1",
        "difficulty": "Easy",
        "blooms_level": "Remember",
        "co_mapping": "CO1",
        "marks": 2,
    },
    {
        "question_text": "Explain the working of a queue with suitable examples.",
        "subject": "Data Structures",
        "unit": "Unit 1",
        "difficulty": "Easy",
        "blooms_level": "Understand",
        "co_mapping": "CO1",
        "marks": 2,
    },
    {
        "question_text": "Implement a circular queue using an array.",
        "subject": "Data Structures",
        "unit": "Unit 2",
        "difficulty": "Medium",
        "blooms_level": "Apply",
        "co_mapping": "CO2",
        "marks": 5,
    },
    {
        "question_text": "Analyze the time complexity of operations on a singly linked list.",
        "subject": "Data Structures",
        "unit": "Unit 2",
        "difficulty": "Medium",
        "blooms_level": "Analyze",
        "co_mapping": "CO2",
        "marks": 5,
    },
    {
        "question_text": "What is a binary tree? Define height, depth, and level of a node.",
        "subject": "Data Structures",
        "unit": "Unit 3",
        "difficulty": "Easy",
        "blooms_level": "Remember",
        "co_mapping": "CO3",
        "marks": 2,
    },
    {
        "question_text": "Explain AVL tree rotations with examples.",
        "subject": "Data Structures",
        "unit": "Unit 3",
        "difficulty": "Hard",
        "blooms_level": "Understand",
        "co_mapping": "CO3",
        "marks": 10,
    },
    {
        "question_text": "Implement Dijkstra's shortest path algorithm.",
        "subject": "Data Structures",
        "unit": "Unit 4",
        "difficulty": "Hard",
        "blooms_level": "Apply",
        "co_mapping": "CO4",
        "marks": 10,
    },
    {
        "question_text": "Compare hashing techniques: open addressing vs. chaining.",
        "subject": "Data Structures",
        "unit": "Unit 4",
        "difficulty": "Medium",
        "blooms_level": "Evaluate",
        "co_mapping": "CO4",
        "marks": 5,
    },
    {
        "question_text": "Design a data structure to implement an LRU cache.",
        "subject": "Data Structures",
        "unit": "Unit 5",
        "difficulty": "Hard",
        "blooms_level": "Create",
        "co_mapping": "CO5",
        "marks": 10,
    },
    {
        "question_text": "Explain BFS and DFS graph traversal algorithms.",
        "subject": "Data Structures",
        "unit": "Unit 4",
        "difficulty": "Medium",
        "blooms_level": "Understand",
        "co_mapping": "CO4",
        "marks": 5,
    },
    # -----------------------------------------------------------------------
    # Database Management Systems
    # -----------------------------------------------------------------------
    {
        "question_text": "Define DBMS and list its advantages over file systems.",
        "subject": "Database Management Systems",
        "unit": "Unit 1",
        "difficulty": "Easy",
        "blooms_level": "Remember",
        "co_mapping": "CO1",
        "marks": 2,
    },
    {
        "question_text": "Explain the three-schema architecture of a DBMS.",
        "subject": "Database Management Systems",
        "unit": "Unit 1",
        "difficulty": "Medium",
        "blooms_level": "Understand",
        "co_mapping": "CO1",
        "marks": 5,
    },
    {
        "question_text": "What is an ER diagram? Draw one for a university database.",
        "subject": "Database Management Systems",
        "unit": "Unit 2",
        "difficulty": "Medium",
        "blooms_level": "Apply",
        "co_mapping": "CO2",
        "marks": 5,
    },
    {
        "question_text": "Explain the different normal forms with examples.",
        "subject": "Database Management Systems",
        "unit": "Unit 3",
        "difficulty": "Hard",
        "blooms_level": "Understand",
        "co_mapping": "CO3",
        "marks": 10,
    },
    {
        "question_text": "Write SQL queries to perform CRUD operations on a student table.",
        "subject": "Database Management Systems",
        "unit": "Unit 3",
        "difficulty": "Easy",
        "blooms_level": "Apply",
        "co_mapping": "CO3",
        "marks": 2,
    },
    {
        "question_text": "Analyze the differences between clustered and non-clustered indexes.",
        "subject": "Database Management Systems",
        "unit": "Unit 4",
        "difficulty": "Medium",
        "blooms_level": "Analyze",
        "co_mapping": "CO4",
        "marks": 5,
    },
    {
        "question_text": "Explain ACID properties of database transactions.",
        "subject": "Database Management Systems",
        "unit": "Unit 4",
        "difficulty": "Easy",
        "blooms_level": "Remember",
        "co_mapping": "CO4",
        "marks": 2,
    },
    {
        "question_text": "Design a relational schema for an e-commerce application.",
        "subject": "Database Management Systems",
        "unit": "Unit 5",
        "difficulty": "Hard",
        "blooms_level": "Create",
        "co_mapping": "CO5",
        "marks": 10,
    },
    {
        "question_text": "Evaluate the trade-offs between SQL and NoSQL databases.",
        "subject": "Database Management Systems",
        "unit": "Unit 5",
        "difficulty": "Hard",
        "blooms_level": "Evaluate",
        "co_mapping": "CO5",
        "marks": 10,
    },
    {
        "question_text": "Explain concurrency control mechanisms in DBMS.",
        "subject": "Database Management Systems",
        "unit": "Unit 4",
        "difficulty": "Medium",
        "blooms_level": "Understand",
        "co_mapping": "CO4",
        "marks": 5,
    },
    # -----------------------------------------------------------------------
    # Operating Systems
    # -----------------------------------------------------------------------
    {
        "question_text": "Define an operating system and list its functions.",
        "subject": "Operating Systems",
        "unit": "Unit 1",
        "difficulty": "Easy",
        "blooms_level": "Remember",
        "co_mapping": "CO1",
        "marks": 2,
    },
    {
        "question_text": "Explain the differences between process and thread.",
        "subject": "Operating Systems",
        "unit": "Unit 1",
        "difficulty": "Easy",
        "blooms_level": "Understand",
        "co_mapping": "CO1",
        "marks": 2,
    },
    {
        "question_text": "Implement the Round Robin scheduling algorithm.",
        "subject": "Operating Systems",
        "unit": "Unit 2",
        "difficulty": "Medium",
        "blooms_level": "Apply",
        "co_mapping": "CO2",
        "marks": 5,
    },
    {
        "question_text": "Analyze the Banker's algorithm for deadlock avoidance.",
        "subject": "Operating Systems",
        "unit": "Unit 3",
        "difficulty": "Hard",
        "blooms_level": "Analyze",
        "co_mapping": "CO3",
        "marks": 10,
    },
    {
        "question_text": "Explain virtual memory and demand paging.",
        "subject": "Operating Systems",
        "unit": "Unit 4",
        "difficulty": "Medium",
        "blooms_level": "Understand",
        "co_mapping": "CO4",
        "marks": 5,
    },
    {
        "question_text": "Compare FIFO, LRU and Optimal page replacement algorithms.",
        "subject": "Operating Systems",
        "unit": "Unit 4",
        "difficulty": "Medium",
        "blooms_level": "Evaluate",
        "co_mapping": "CO4",
        "marks": 5,
    },
    {
        "question_text": "Design a solution for the Producer-Consumer problem using semaphores.",
        "subject": "Operating Systems",
        "unit": "Unit 3",
        "difficulty": "Hard",
        "blooms_level": "Create",
        "co_mapping": "CO3",
        "marks": 10,
    },
    {
        "question_text": "What are the four necessary conditions for deadlock?",
        "subject": "Operating Systems",
        "unit": "Unit 3",
        "difficulty": "Easy",
        "blooms_level": "Remember",
        "co_mapping": "CO3",
        "marks": 2,
    },
    # -----------------------------------------------------------------------
    # Software Engineering
    # -----------------------------------------------------------------------
    {
        "question_text": "Define Software Engineering and its importance.",
        "subject": "Software Engineering",
        "unit": "Unit 1",
        "difficulty": "Easy",
        "blooms_level": "Remember",
        "co_mapping": "CO1",
        "marks": 2,
    },
    {
        "question_text": "Explain the Waterfall model of software development.",
        "subject": "Software Engineering",
        "unit": "Unit 1",
        "difficulty": "Easy",
        "blooms_level": "Understand",
        "co_mapping": "CO1",
        "marks": 2,
    },
    {
        "question_text": "Compare Agile and Waterfall software development methodologies.",
        "subject": "Software Engineering",
        "unit": "Unit 2",
        "difficulty": "Medium",
        "blooms_level": "Analyze",
        "co_mapping": "CO2",
        "marks": 5,
    },
    {
        "question_text": "Explain the concept of cohesion and coupling in software design.",
        "subject": "Software Engineering",
        "unit": "Unit 3",
        "difficulty": "Medium",
        "blooms_level": "Understand",
        "co_mapping": "CO3",
        "marks": 5,
    },
    {
        "question_text": "Design a UML class diagram for a banking application.",
        "subject": "Software Engineering",
        "unit": "Unit 3",
        "difficulty": "Hard",
        "blooms_level": "Create",
        "co_mapping": "CO3",
        "marks": 10,
    },
    {
        "question_text": "Explain different types of software testing.",
        "subject": "Software Engineering",
        "unit": "Unit 4",
        "difficulty": "Easy",
        "blooms_level": "Remember",
        "co_mapping": "CO4",
        "marks": 2,
    },
    {
        "question_text": "Evaluate the effectiveness of black-box vs white-box testing.",
        "subject": "Software Engineering",
        "unit": "Unit 4",
        "difficulty": "Hard",
        "blooms_level": "Evaluate",
        "co_mapping": "CO4",
        "marks": 10,
    },
    # -----------------------------------------------------------------------
    # Mathematics
    # -----------------------------------------------------------------------
    {
        "question_text": "Define a group and give an example.",
        "subject": "Mathematics",
        "unit": "Unit 1",
        "difficulty": "Easy",
        "blooms_level": "Remember",
        "co_mapping": "CO1",
        "marks": 2,
    },
    {
        "question_text": "Prove that the set of integers under addition forms a group.",
        "subject": "Mathematics",
        "unit": "Unit 1",
        "difficulty": "Medium",
        "blooms_level": "Apply",
        "co_mapping": "CO1",
        "marks": 5,
    },
    {
        "question_text": "Explain Bayes' theorem and apply it to a real-world problem.",
        "subject": "Mathematics",
        "unit": "Unit 2",
        "difficulty": "Medium",
        "blooms_level": "Apply",
        "co_mapping": "CO2",
        "marks": 5,
    },
    {
        "question_text": "Find the eigenvalues and eigenvectors of a given 3x3 matrix.",
        "subject": "Mathematics",
        "unit": "Unit 3",
        "difficulty": "Hard",
        "blooms_level": "Analyze",
        "co_mapping": "CO3",
        "marks": 10,
    },
    {
        "question_text": "State and prove the Cauchy-Schwarz inequality.",
        "subject": "Mathematics",
        "unit": "Unit 4",
        "difficulty": "Hard",
        "blooms_level": "Evaluate",
        "co_mapping": "CO4",
        "marks": 10,
    },
    {
        "question_text": "Solve a system of linear equations using Gaussian elimination.",
        "subject": "Mathematics",
        "unit": "Unit 3",
        "difficulty": "Medium",
        "blooms_level": "Apply",
        "co_mapping": "CO3",
        "marks": 5,
    },
]


def load_sample_data():
    """Insert sample questions into the database."""
    with app.app_context():
        db.create_all()

        # Avoid inserting duplicates if already loaded
        if Question.query.count() > 0:
            print("Database already has questions. Skipping sample data load.")
            return

        for q_data in SAMPLE_QUESTIONS:
            question = Question(**q_data)
            db.session.add(question)

        db.session.commit()
        print(f"Loaded {len(SAMPLE_QUESTIONS)} sample questions into the database.")


if __name__ == "__main__":
    load_sample_data()
