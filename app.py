from flask import Flask, render_template, request, redirect, url_for, session
import json
import re

app = Flask(__name__)

# Load questions from the JSON file
def load_questions():
    """This function loads the quiz questions from the JSON file."""
    with open('questions.json', 'r') as file:
        data = json.load(file)
    return data['questions']

app.secret_key = 'your_secret_key'  # Secret key to encrypt session cookies

def normalize_answer(ans):
    """Normalize answers by removing LaTeX delimiters \( \), spaces, and lowercasing."""
    if not ans:
        return ''
    # Remove LaTeX delimiters \( and \)
    ans = re.sub(r'\\\(|\\\)', '', ans)
    # Remove spaces and convert to lowercase
    ans = ans.replace(' ', '').lower()
    return ans

# Initialize session variables
@app.before_request
def before_request():
    """This function ensures that session variables for score and question tracking are initialized."""
    if 'score' not in session: 
        session['score'] = 0 
    if 'current_question' not in session:
        session['current_question'] = 0  
    if 'answers' not in session:
        session['answers'] = []

@app.route('/', methods=['GET', 'POST'])
def index():
    """This route displays a question, checks answers, and moves to the next question."""
    questions = load_questions()
    current_question_index = session['current_question']  

    # If all questions are answered, display the final score
    if current_question_index >= len(questions):
        return render_template('final_score.html', score=session['score'], total=len(questions))

    # Get the current question object
    question = questions[current_question_index]
    
    if request.method == 'POST':
        user_answer = request.form.get('user_answer', '').strip()
        correct_answer = question['correct_answer'].strip()
        
        # Normalize and compare answers
        is_correct = normalize_answer(user_answer) == normalize_answer(correct_answer)
        if is_correct:
            session['score'] += 1 
        
        # Save the user's answer and its correctness in the session
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

# Final Score
@app.route('/final_score')
def final_score():
    """This route displays the final score of the user after completing all questions."""
    questions = load_questions()
    return render_template('final_score.html', score=session['score'], total=len(questions))

# Route to restart the quiz
@app.route('/restart')
def restart():
    """This route clears the session to restart the quiz."""
    session.clear() 
    return redirect(url_for('index'))

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
