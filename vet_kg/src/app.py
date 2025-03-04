from flask import Flask, render_template, request, jsonify
from vet_chatbot import VetPharmacyBot
import logging

app = Flask(__name__)
bot = VetPharmacyBot()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/query', methods=['POST'])
def query():
    try:
        user_query = request.json['query']
        response = bot.process_query(user_query)
        return jsonify({'response': response})
    except Exception as e:
        logging.error(f"Error processing query: {str(e)}")
        return jsonify({'response': "I'm sorry, I encountered an error processing your query."}), 500

@app.teardown_appcontext
def cleanup(error):
    bot.close()

if __name__ == '__main__':
    app.run(debug=True) 