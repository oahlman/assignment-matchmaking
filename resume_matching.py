
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import string

def refined_preprocess_text(text):
    """
    Clean and preprocess the text.
    """
    # Convert to lowercase
    text = text.lower()
    # Remove punctuation (but retain hyphens as they might be relevant in job-related contexts)
    translator = str.maketrans('', '', string.punctuation.replace('-', ''))
    text = text.translate(translator)
    # Strip white spaces
    text = text.strip()
    return text

def fetch_texts_from_directory(directory):
    """
    Fetch all texts from .txt files in the specified directory.

    Parameters:
    - directory (str): Directory to fetch .txt files from.

    Returns:
    - list: List of texts from the .txt files.
    """
    texts = []
    for filename in os.listdir(directory):
        if filename.endswith(".txt"):
            with open(os.path.join(directory, filename), 'r', encoding='utf-8') as file:
                texts.append(file.read())
    return texts

def compute_similarity(resume_texts, job_ad_texts):
    """
    Compute similarity between resumes and job ads using TF-IDF and Cosine Similarity.
    
    Parameters:
    - resume_texts (list of str): List of resume texts.
    - job_ad_texts (list of str): List of job ad texts.
    
    Returns:
    - dict: A dictionary where keys are job ad indices and values are lists of tuples 
            (resume index, similarity score) sorted in descending order of similarity.
    """
    # Combine resume and job ad texts
    combined_texts = resume_texts + job_ad_texts
    # Vectorize the texts using TF-IDF
    vectorizer = TfidfVectorizer(stop_words='english', preprocessor=refined_preprocess_text)
    tfidf_matrix = vectorizer.fit_transform(combined_texts)
    # Split the matrix into resume and job ad matrices
    resume_matrix = tfidf_matrix[:len(resume_texts)]
    job_ad_matrix = tfidf_matrix[len(resume_texts):]
    # Compute cosine similarity between resumes and job ads
    similarity_scores = cosine_similarity(resume_matrix, job_ad_matrix)
    # Create a dictionary to store ranked resumes for each job ad
    ranked_resumes = {}
    for job_index in range(similarity_scores.shape[1]):
        ranked_resumes[job_index] = sorted(enumerate(similarity_scores[:, job_index]), key=lambda x: x[1], reverse=True)
    return ranked_resumes

def save_ranked_resumes_with_names_to_directory(ranked_resumes, directory, assignment_filenames, resume_filenames):
    """
    Save the ranked resume filenames for each assignment to the specified directory.

    Parameters:
    - ranked_resumes (dict): Dictionary with keys as assignment indices and values as lists of tuples 
                             (resume index, similarity score).
    - directory (str): Directory to save the ranked resumes.
    - assignment_filenames (list): List of assignment filenames to use for saving the results.
    - resume_filenames (list): List of resume filenames to correlate with the rankings.
    """
    os.makedirs(directory, exist_ok=True)
    for assignment_index, rankings in ranked_resumes.items():
        output_filename = assignment_filenames[assignment_index].replace(".txt", "_ranked_resumes.txt")
        with open(os.path.join(directory, output_filename), 'w', encoding='utf-8') as file:
            for resume_index, score in rankings:
                file.write(f"{resume_filenames[resume_index]} - Score: {score:.4f}\n")

# Fetch resume and assignment texts
resume_texts = fetch_texts_from_directory("../cv-txt")
assignment_texts = fetch_texts_from_directory("../assignment-txt")
# Fetch resume filenames
resume_filenames = [filename for filename in os.listdir("../cv-txt") if filename.endswith(".txt")]
# Compute similarity between resumes and assignments
ranked_resumes = compute_similarity(resume_texts, assignment_texts)
# Save the ranked resumes for each assignment to the "assignment-match" directory

# Fetch assignment filenames
assignment_filenames = [filename for filename in os.listdir("../assignment-txt") if filename.endswith(".txt")]
# Save the ranked resumes for each assignment to the "assignment-match" directory
save_ranked_resumes_with_names_to_directory(ranked_resumes, "../assignment-match", assignment_filenames, resume_filenames)

