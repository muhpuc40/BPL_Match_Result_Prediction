from flask import Flask, request, render_template
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from xgboost import XGBClassifier
import joblib

app = Flask(__name__)

# Load the dataset and train the model
df = pd.read_csv('bpl_processed.csv')  # Replace with your dataset file

# Prepare the features (X) and the target variable (y)
X = df[['season','match_no', 'team_1', 'team_1_score', 'team_1_wicket', 'team_2',
       'team_2_score', 'team_2_wicket',  'toss_winner',
       'toss_decision', 'venue', 'city','umpire_1','umpire_2']]
y = df['winner']

# Convert categorical variables to numeric using one-hot encoding
X = pd.get_dummies(X)
label_encoder = LabelEncoder()
y = label_encoder.fit_transform(y)

# Split the data into training and test sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.1, random_state=5)

# Train the XGBoost model
model = XGBClassifier()
model.fit(X_train, y_train)

# Save the trained model (optional)
joblib.dump(model, 'xgb_model.pkl')

@app.route('/')
def home():
    return render_template('index.html')  # Corrected template name

@app.route('/predict', methods=['POST'])
def predict():
    # Get form data
    season = request.form['season']
    team_1 = request.form['team_1']
    team_1_score = int(request.form['team_1_score'])
    team_1_wicket = int(request.form['team_1_wicket'])
    team_2 = request.form['team_2']
    toss_winner = request.form['toss_winner']
    toss_decision = request.form['toss_decision']
    city = request.form['city']
    venue = request.form['venue']
    umpire_1 = request.form['umpire_1']
    umpire_2 = request.form['umpire_2']

    # Prepare input data for prediction
    input_data = {
        'season': [season],
        'team_1': [team_1],
        'team_1_score': [team_1_score],
        'team_1_wicket': [team_1_wicket],
        'team_2': [team_2],
        'toss_winner': [toss_winner],
        'toss_decision': [toss_decision],
        'city': [city],
        'venue': [venue],
        'umpire_1': [umpire_1],
        'umpire_2': [umpire_2]
    }

    input_df = pd.DataFrame(input_data)
    input_df = pd.get_dummies(input_df)

    # Align the input data with training data columns
    input_df = input_df.reindex(columns=X.columns, fill_value=0)

    # Load the trained model
    model = joblib.load('xgb_model.pkl')

    # Predict the winner
    predicted_winner_encoded = model.predict(input_df)
    predicted_winner = label_encoder.inverse_transform(predicted_winner_encoded)

    # Return result page with predicted winner
    return render_template('index.html', winner=predicted_winner[0])  # Corrected template name

if __name__ == "__main__":
    app.run(debug=True)
