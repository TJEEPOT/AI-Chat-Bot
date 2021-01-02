from flask import Flask,render_template,request, jsonify, make_response

app = Flask(__name__)

@app.route("/")
def home():
    return render_template('interface.html')

@app.route("/get_reply", methods=['POST'])
def get_reply():

    if request.method == 'POST':
        userInput = request.get_json()
        print(userInput)
        response = make_response(jsonify({"message": generate_response(userInput)}), 200)
        return response

# main logic function calling other modules
def generate_response(userInput):
    return userInput.upper()
if __name__ == "__main__":
    app.run()
