from flask import Flask, render_template, request, redirect, url_for, session
import json
import re

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Secret key to encrypt session cookies

# Load questions from the JSON file
def load_questions():
    """This function loads the quiz questions from the JSON file."""
    with open('questions.json', 'r') as file:
        data = json.load(file)
    return data['questions']

# Normalize answers for comparison
def normalize_answer(ans):
    """Normalize answers by removing LaTeX delimiters, formatting, and units."""
    if not ans:
        return ''
    # Remove LaTeX math delimiters $$...$$ and \( \)
    ans = re.sub(r'\$\$|\$|\\\(|\\\)', '', ans)
    # Remove LaTeX formatting commands like \text{}
    ans = re.sub(r'\\text\{([^}]*)\}', r'\1', ans)
    # Remove superscript and subscript markers
    ans = re.sub(r'\^|_', '', ans)
    # Remove units like cm, cm2, etc.
    ans = re.sub(r'\s*cm\^?2?', '', ans, flags=re.IGNORECASE)
    # Remove all whitespace and lowercase
    ans = ans.replace(' ', '').lower()
    return ans

# Initialize session variables
@app.before_request
def before_request():
    """Ensure session variables are initialized."""
    if 'score' not in session:
        session['score'] = 0
    if 'current_question' not in session:
        session['current_question'] = 0
    if 'answers' not in session:
        session['answers'] = []

@app.route('/', methods=['GET', 'POST'])
def index():
    """Main route to display questions and process answers."""
    questions = load_questions()
    current_question_index = session['current_question']

    # If all questions are answered, show final score
    if current_question_index >= len(questions):
        return redirect(url_for('final_score'))

    question = questions[current_question_index]

    if request.method == 'POST':
        user_answer = request.form.get('user_answer', '').strip()
        correct_answer = question['correct_answer'].strip()

        # Normalize and compare answers
        is_correct = normalize_answer(user_answer) == normalize_answer(correct_answer)
        if is_correct:
            session['score'] += 1

        # Save answer details
        answers = session.get('answers', [])
        answers.append({
            'question': question['question'],
            'user_answer': user_answer,
            'correct_answer': correct_answer,
            'is_correct': is_correct
        })
        session['answers'] = answers
        session['current_question'] += 1

        return redirect(url_for('index'))

    return render_template('index.html', question=question, index=current_question_index)

@app.route('/final_score')
def final_score():
    """Display the final score and summary."""
    questions = load_questions()
    return render_template('final_score.html', score=session['score'], total=len(questions), answers=session['answers'])

@app.route('/restart')
def restart():
    """Restart the quiz by clearing the session."""
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, port=5005)