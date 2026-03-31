from preprocessing import preprocess_syllabus
from generator import generate_questions
from similarity import remove_similar_questions
from tagging import tag_questions
from validator import *
from paper_assembly import assemble_paper
from export import export_pdf, export_docx

syllabus = "Blockchain features, consensus mechanisms, hashing, distributed systems"

data = preprocess_syllabus(syllabus)

questions = generate_questions(data["keywords"], "Analyze", 6)

questions = remove_similar_questions(questions)

co_map = {concept: "CO1" for concept in data["keywords"]}

questions = tag_questions(questions, co_map)

paper = assemble_paper(questions, "Blockchain Technology")

export_pdf(paper)
export_docx(paper)