from flask import Flask, render_template, request, redirect, url_for
import json

app = Flask(__name__)

# Load questions from the JSON file
def load_questions():
    with open('questions.json', 'r') as file:
        data = json.load(file)
    return data['questions']

# Store user answers in a session (so they persist between requests)
# You can use Flask session to store user data like scores
from flask import session

app.secret_key = 'your_secret_key'  # Needed for session to work

# Initialize user's data (score, current question index, etc.)
@app.before_request
def before_request():
    if 'score' not in session:
        session['score'] = 0
        session['current_question'] = 0
        session['answers'] = []

# Route to display the question and get user input
@app.route('/', methods=['GET', 'POST'])
def index():
    questions = load_questions()
    current_question_index = session['current_question']
    
    if current_question_index >= len(questions):
        # If all questions are answered, show the final score
        return render_template('final_score.html', score=session['score'], total=len(questions))

    question = questions[current_question_index]
    
    if request.method == 'POST':
        user_answer = request.form['user_answer']
        correct_answer = question['correct_answer']
        
        # Check if the answer is correct
        if user_answer == correct_answer:
            session['score'] += 1
        
        # Save the answer to the answers list
        session['answers'].append({
            'question': question['question'],
            'user_answer': user_answer,
            'correct_answer': correct_answer,
            'is_correct': user_answer == correct_answer
        })
        
        # Move to the next question
        session['current_question'] += 1
        
        return redirect(url_for('index'))
    
    return render_template('index.html', question=question, index=current_question_index)

# Route to show the final score after all questions are answered
@app.route('/final_score')
def final_score():
    questions = load_questions()
    return render_template('final_score.html', score=session['score'], total=len(questions))

if __name__ == '__main__':
    app.run(debug=True)
