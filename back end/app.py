from flask import Flask, request, jsonify, render_template_string
import json
from datetime import datetime

app = Flask(__name__)

# HTML Template for the chatbot interface
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Diabetes Diet Recommender Chatbot</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            margin: 0;
            padding: 20px;
            min-height: 100vh;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            overflow: hidden;
        }
        .header {
            background: #2c3e50;
            color: white;
            padding: 20px;
            text-align: center;
        }
        .chat-container {
            height: 400px;
            overflow-y: auto;
            padding: 20px;
            background: #f8f9fa;
        }
        .message {
            margin-bottom: 15px;
            padding: 12px 18px;
            border-radius: 20px;
            max-width: 80%;
        }
        .bot-message {
            background: #e3f2fd;
            border: 2px solid #2196f3;
            align-self: flex-start;
        }
        .user-message {
            background: #e8f5e8;
            border: 2px solid #4caf50;
            margin-left: auto;
            text-align: right;
        }
        .input-container {
            padding: 20px;
            background: white;
            border-top: 1px solid #eee;
            display: flex;
            gap: 10px;
        }
        input[type="text"] {
            flex: 1;
            padding: 12px;
            border: 2px solid #ddd;
            border-radius: 25px;
            font-size: 16px;
        }
        button {
            padding: 12px 24px;
            background: #4caf50;
            color: white;
            border: none;
            border-radius: 25px;
            cursor: pointer;
            font-size: 16px;
        }
        button:hover {
            background: #45a049;
        }
        .recommendation-card {
            background: #f0f8ff;
            border: 2px solid #4169e1;
            border-radius: 10px;
            padding: 15px;
            margin: 10px 0;
        }
        .bmi-display {
            background: #fff3cd;
            border: 2px solid #ffc107;
            border-radius: 8px;
            padding: 10px;
            margin: 5px 0;
            font-weight: bold;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>DiabEat🍎</h1>
            <p>Get personalized diet recommendations based on your health data</p>
        </div>
        <div class="chat-container" id="chatContainer">
            <div class="message bot-message">
                <strong>Bot:</strong> Welcome! I'm here to help you get personalized diet recommendations for diabetes management. Let's start by collecting some basic information.<br><br>
                Please provide your <strong>age</strong>:
            </div>
        </div>
        <div class="input-container">
            <input type="text" id="userInput" placeholder="Type your response here..." onkeypress="handleKeyPress(event)">
            <button onclick="sendMessage()">Send</button>
        </div>
    </div>

    <script>
        let currentStep = 'age';
        let userData = {};

        function handleKeyPress(event) {
            if (event.key === 'Enter') {
                sendMessage();
            }
        }

        function addMessage(sender, message, isHtml = false) {
            const chatContainer = document.getElementById('chatContainer');
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${sender}-message`;

            if (isHtml) {
                messageDiv.innerHTML = `<strong>${sender.charAt(0).toUpperCase() + sender.slice(1)}:</strong> ${message}`;
            } else {
                messageDiv.innerHTML = `<strong>${sender.charAt(0).toUpperCase() + sender.slice(1)}:</strong> ${message}`;

            }

            chatContainer.appendChild(messageDiv);
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }

        function sendMessage() {
            const input = document.getElementById('userInput');
            const userInput = input.value.trim();

            if (!userInput) return;

            addMessage('user', userInput);
            input.value = '';

            // Process user input based on current step
            processUserInput(userInput);
        }

        function processUserInput(input) {
    switch(currentStep) {
        case 'age':
            if (isNaN(input) || input < 1 || input > 120) {
                addMessage('bot', 'Please enter a valid age (1-120 years):');
                return;
            }
            userData.age = parseInt(input);
            currentStep = 'sugar';
            addMessage('bot', 'Great! Now please provide your <strong>sugar level</strong> (mg/dL):', true);
            break;

        case 'sugar':
            if (isNaN(input) || input < 50 || input > 500) {
                addMessage('bot', 'Please enter a valid sugar level (50-500 mg/dL):');
                return;
            }
            userData.sugar = parseInt(input);
            currentStep = 'diabetes_type';
            addMessage('bot', 'What type of <strong>diabetes</strong> do you have?<br>Type: <strong>Type 1</strong>, <strong>Type 2</strong>, or <strong>Gestational</strong>', true);
            break;

        case 'diabetes_type':
            const validTypes = ['type 1', 'type 2', 'gestational'];
            const lower = input.toLowerCase();
            if (!validTypes.includes(lower)) {
                addMessage('bot', 'Please enter one of the following: Type 1, Type 2, or Gestational.');
                return;
            }
            userData.diabetes_type = lower;
            currentStep = 'bp';
            addMessage('bot', 'Thank you! What is your <strong>blood pressure status</strong>?<br>Type: normal, high, or low:', true);
            break;

                case 'bp':
                    const validBP = ['normal', 'high', 'low'];
                    if (!validBP.includes(input.toLowerCase())) {
                        addMessage('bot', 'Please enter a valid blood pressure status: normal, high, or low');
                        return;
                    }
                    userData.bp = input.toLowerCase();
                    currentStep = 'weight';
                    addMessage('bot', 'Perfect! Please provide your <strong>weight</strong> (in kg):', true);
                    break;

                case 'weight':
                    if (isNaN(input) || input < 20 || input > 300) {
                        addMessage('bot', 'Please enter a valid weight (20-300 kg):');
                        return;
                    }
                    userData.weight = parseFloat(input);
                    currentStep = 'height';
                    addMessage('bot', 'Excellent! Now please provide your <strong>height</strong> (in cm):', true);
                    break;

                case 'height':
                    if (isNaN(input) || input < 100 || input > 250) {
                        addMessage('bot', 'Please enter a valid height (100-250 cm):');
                        return;
                    }
                    userData.height = parseFloat(input);
                    currentStep = 'preference';
                    addMessage('bot', 'Almost done! What is your <strong>diet preference</strong>?<br>Type: veg (vegetarian) or nonveg (non-vegetarian):', true);
                    break;

                case 'preference':
                    const validPrefs = ['veg', 'nonveg', 'vegetarian', 'non-vegetarian'];
                    if (!validPrefs.includes(input.toLowerCase())) {
                        addMessage('bot', 'Please enter a valid diet preference: veg or nonveg');
                        return;
                    }
                    userData.preference = input.toLowerCase().includes('veg') && !input.toLowerCase().includes('nonveg') ? 'veg' : 'nonveg';

                    // Calculate recommendations
                    generateRecommendations();
                    break;
            }
        }

        function generateRecommendations() {
    const heightM = userData.height / 100;
    const bmi = (userData.weight / (heightM * heightM)).toFixed(2);

    let healthNote = '';
    if (userData.sugar < 100) {
        healthNote = 'Normal sugar levels - maintain balanced diet';
    } else if (userData.sugar <= 125) {
        healthNote = 'Pre-diabetic range - focus on low GI foods';
    } else if (userData.sugar <= 180) {
        healthNote = 'Slightly high sugar - eat complex carbs, avoid simple sugars';
    } else {
        healthNote = 'High sugar levels - strict low-carb diet recommended, consult doctor';
    }

    // Custom meals based on diabetes type
    let breakfast, lunch, dinner;

    const t = userData.diabetes_type;
    const pref = userData.preference;

    if (t === 'type 1') {
        breakfast = pref === 'veg' ? 'Moong dal chilla + Mint chutney' : 'Egg sandwich with whole wheat bread';
        lunch = pref === 'veg' ? 'Mixed veg curry + 2 chapatis + Salad' : 'Grilled chicken + Brown rice + Beans';
        dinner = pref === 'veg' ? 'Vegetable soup + Paneer tikka' : 'Chicken stew + Steamed veggies';
    } else if (t === 'type 2') {
        breakfast = pref === 'veg' ? 'Oats porridge + Apple' : 'Boiled eggs + Avocado toast';
        lunch = pref === 'veg' ? 'Spinach dal + Quinoa + Curd' : 'Fish curry + Red rice + Salad';
        dinner = pref === 'veg' ? 'Tofu stir fry + Methi soup' : 'Grilled salmon + Green beans + Soup';
    } else if (t === 'gestational') {
        breakfast = pref === 'veg' ? 'Ragi dosa + Coconut chutney' : 'Omelette + Multigrain toast';
        lunch = pref === 'veg' ? 'Lentil soup + Brown rice + Mixed veg' : 'Grilled chicken breast + Veg soup';
        dinner = pref === 'veg' ? 'Vegetable khichdi + Buttermilk' : 'Fish with sautéed spinach + Roti';
    }

    const results = `
        <div class="recommendation-card">
            <h3>🎯 Your Personalized Diet Plan</h3>
            <div class="bmi-display">
                <strong>BMI:</strong> ${bmi} kg/m²
            </div>
            <p><strong>🧬 Diabetes Type:</strong> ${userData.diabetes_type.charAt(0).toUpperCase() + userData.diabetes_type.slice(1)}</p>
            <p><strong>📝 Health Note:</strong> ${healthNote}</p>

            <h4>🍳 Recommended Breakfast:</h4>
            <p>${breakfast}</p>

            <h4>🍽️ Recommended Lunch:</h4>
            <p>${lunch}</p>

            <h4>🌙 Recommended Dinner:</h4>
            <p>${dinner}</p>

            <div style="margin-top: 15px; padding: 10px; background: #e8f5e8; border-radius: 5px;">
                <strong>💡 Additional Tips:</strong>
                <ul>
                    <li>Follow a consistent meal schedule</li>
                    <li>Monitor sugar levels daily</li>
                    <li>Exercise for 30 mins/day (walking, yoga)</li>
                    <li>Stay hydrated and reduce stress</li>
                    <li>Consult your doctor regularly</li>
                </ul>
            </div>
        </div>
    `;

    addMessage('bot', results, true);

    setTimeout(() => {
        addMessage('bot', 'Would you like to get another recommendation? If yes, please provide your <strong>age</strong> to start again:', true);
        currentStep = 'age';
        userData = {};
    }, 2000);
}

    </script>
</body>
</html>
"""

class DiabetesDietChatbot:
    def __init__(self):
        self.user_data = {}

    def calculate_bmi(self, weight, height):
        """Calculate BMI from weight (kg) and height (cm)"""
        height_m = height / 100
        bmi = weight / (height_m ** 2)
        return round(bmi, 2)

    def get_health_note(self, sugar_level):
        """Generate health note based on sugar level"""
        if sugar_level < 100:
            return "Normal sugar levels - maintain balanced diet"
        elif sugar_level <= 125:
            return "Pre-diabetic range - focus on low GI foods"
        elif sugar_level <= 180:
            return "Slightly high sugar - eat complex carbs, avoid simple sugars"
        else:
            return "High sugar levels - strict low-carb diet recommended, consult doctor"

    def get_vegetarian_recommendations(self, sugar_level):
        """Get vegetarian meal recommendations based on sugar level"""
        if sugar_level <= 125:
            return {
                'breakfast': 'Oats with almonds and cinnamon + Green tea',
                'lunch': 'Brown rice (small portion) + Mixed vegetable curry + Salad',
                'dinner': 'Grilled paneer/tofu + Steamed vegetables + Clear soup'
            }
        else:
            return {
                'breakfast': 'Vegetable omelette (with minimal oil) + Herbal tea',
                'lunch': 'Quinoa + Spinach dal + Cucumber salad',
                'dinner': 'Grilled cottage cheese + Broccoli + Tomato soup'
            }

    def get_nonvegetarian_recommendations(self, sugar_level):
        """Get non-vegetarian meal recommendations based on sugar level"""
        if sugar_level <= 125:
            return {
                'breakfast': 'Boiled eggs (2) + Avocado + Green tea',
                'lunch': 'Grilled chicken breast + Brown rice (small) + Salad',
                'dinner': 'Fish curry (less oil) + Steamed vegetables'
            }
        else:
            return {
                'breakfast': 'Egg white omelette + Spinach + Black coffee',
                'lunch': 'Grilled salmon + Cauliflower rice + Green salad',
                'dinner': 'Chicken soup + Steamed broccoli + Mixed greens'
            }

    def generate_recommendations(self, user_data):
        """Generate complete diet recommendations"""
        # Calculate BMI
        bmi = self.calculate_bmi(user_data['weight'], user_data['height'])

        # Get health note
        health_note = self.get_health_note(user_data['sugar'])

        # Get meal recommendations based on preference
        if user_data['preference'] == 'veg':
            meals = self.get_vegetarian_recommendations(user_data['sugar'])
        else:
            meals = self.get_nonvegetarian_recommendations(user_data['sugar'])

        return {
            'bmi': bmi,
            'health_note': health_note,
            'breakfast': meals['breakfast'],
            'lunch': meals['lunch'],
            'dinner': meals['dinner']
        }

# Flask routes
@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/recommend', methods=['POST'])
def recommend():
    """API endpoint for generating recommendations"""
    try:
        data = request.json
        chatbot = DiabetesDietChatbot()

        # Validate input data
        required_fields = ['age', 'sugar', 'bp', 'weight', 'height', 'preference']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing field: {field}'}), 400

        recommendations = chatbot.generate_recommendations(data)

        return jsonify({
            'status': 'success',
            'data': recommendations
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

if __name__ == '__main__':
    print("🍎 Diabetes Diet Recommender Chatbot Starting...")
    print("📝 Features:")
    print("   - Interactive chatbot interface")
    print("   - BMI calculation")
    print("   - Personalized diet recommendations")
    print("   - Vegetarian and non-vegetarian options")
    print("   - Blood sugar level assessment")
    print("🌐 Access the chatbot at: http://localhost:5000")
    print("🔧 API endpoint available at: http://localhost:5000/api/recommend")
    app.run(debug=True, host='0.0.0.0', port=5000)
    
    import os

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))