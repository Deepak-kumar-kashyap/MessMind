# MessMind — Campus Canteen Demand Predictor

**CA Project | Python Programming + MongoDB + Machine Learning Regression**

MessMind is a Campus Canteen Demand Predictor that estimates the number of food plates required based on the day, meal, food item, weather condition and campus event.

The project uses Python for programming and machine learning, MongoDB for storing records, and a simple web interface for entering inputs and viewing predictions.

The main objective is to demonstrate how machine learning can support better food preparation planning and help reduce possible food wastage or food shortages.

## CA Requirements Covered

- Python programming
- MongoDB backend using PyMongo
- Dataset-based machine learning
- Regression algorithm implementation
- 70/30 training and testing split
- Prediction on unseen test records
- Model evaluation using MAE, RMSE and R²

## Important Dataset Note

The project includes `backend/dataset.csv`, which contains **3,000 synthetic demonstration records** generated using `generate_data.py`.

These records are created for demonstrating the complete machine learning workflow. They are not collected from an actual college canteen.

Therefore, the evaluation metrics represent performance on this generated sample dataset only. They should not be treated as proof of real-world canteen prediction accuracy.

For practical use, the project would need genuine historical canteen sales data.

A possible public dataset reference for future improvement is the [Genpact Food Demand Forecasting dataset](https://datahack.analyticsvidhya.com/contest/genpact-machine-learning-hackathon-1/).

---

## 1. Project Features

- Predicts estimated food demand in number of plates.
- Accepts five input features: day, meal, food item, weather and campus event.
- Uses Random Forest Regression for prediction.
- Displays model evaluation metrics.
- Stores training records and prediction history in MongoDB.
- Provides a simple and user-friendly web interface.
- Allows users to view recent prediction records.

## 2. Technologies Used

| Technology | Purpose |
|---|---|
| Python | Main programming language |
| Pandas | Dataset handling and processing |
| NumPy | Numerical operations |
| Scikit-learn | Machine learning and model evaluation |
| Random Forest Regressor | Demand prediction algorithm |
| MongoDB | Database for storing records |
| PyMongo | Python connection with MongoDB |
| FastAPI | Backend API development |
| Uvicorn | Runs the FastAPI application |
| HTML | Frontend structure |
| CSS | Frontend styling |
| JavaScript | Frontend interactions |

## 3. Project Structure

```text
MessMind_CA_Project/
│
├── backend/
│   ├── app.py                  # FastAPI application and endpoints
│   ├── database.py             # MongoDB connection using PyMongo
│   ├── dataset.csv             # 3,000 synthetic sample records
│   ├── generate_data.py        # Generates demonstration dataset
│   ├── model.py                # Loads model and makes predictions
│   ├── train_model.py          # Model training and evaluation
│   ├── test_predictions.csv    # Actual vs predicted test values
│   ├── model.joblib            # Saved trained model and metrics
│   ├── seed_database.py        # Imports dataset into MongoDB
│   ├── requirements.txt        # Python dependencies
│   └── .env.example            # Example environment configuration
│
└── frontend/
    ├── index.html              # Web application structure
    ├── style.css               # Frontend design
    └── script.js               # Frontend functionality
```

## 4. Dataset Description

The dataset contains 3,000 generated records.

Each record contains the following columns:

| Column | Description |
|---|---|
| day | Day of the week |
| meal | Breakfast, lunch or dinner |
| item | Selected food item |
| weather | Weather condition |
| event | Indicates whether a campus event is happening |
| demand | Estimated number of plates |

The first five columns are input features, while `demand` is the target variable.

Since the target is a numerical value, this project uses regression.

## 5. Machine Learning Algorithm

### Random Forest Regression

MessMind uses the `RandomForestRegressor` algorithm from the Scikit-learn library.

Random Forest is an ensemble learning algorithm that combines multiple decision trees to generate a final prediction.

In simple words, multiple decision trees make predictions, and their outputs are combined to produce the final estimated demand.

### Why Random Forest?

- It can learn patterns from different input features.
- It can handle complex relationships between inputs.
- It is suitable for predicting numerical values.
- It combines multiple decision trees instead of relying on only one tree.

### Model Input and Output

**Input features:**
- Day
- Meal
- Food item
- Weather
- Campus event

**Output:**
- Predicted number of plates.

### One-Hot Encoding

The input features contain categorical values such as Monday, Tuesday, Breakfast and Lunch.

Machine learning models require numerical representations of these categories.

Therefore, the project uses One-Hot Encoding to convert categorical values into numerical columns before training and prediction.

## 6. Training and Testing the Model

Open a terminal inside the `backend` folder.

### Install dependencies

```powershell
python -m pip install -r requirements.txt
```

### Train the model

```powershell
python train_model.py
```

The training script performs the following operations:

1. Reads the dataset using Pandas.
2. Separates input features and target values.
3. Splits the dataset into training and testing data.
4. Converts categorical features using One-Hot Encoding.
5. Trains the Random Forest Regression model.
6. Evaluates predictions using MAE, RMSE and R².
7. Saves the trained model and evaluation metrics in `model.joblib`.
8. Exports actual and predicted test values to `test_predictions.csv`.

### Train-Test Split

The project uses a **70/30 train-test split**.

| Dataset portion | Records | Percentage |
|---|---:|---:|
| Training data | 2,100 | 70% |
| Testing data | 900 | 30% |
| Total | 3,000 | 100% |

The training data is used by the model to learn patterns.

The testing data is kept separate and used to check how well the model predicts values it has not seen during training.

## 7. Model Evaluation Results

The following results were obtained from a training run using the included dataset.

| Evaluation Metric | Result |
|---|---:|
| Total dataset records | 3,000 |
| Training records | 2,100 |
| Testing records | 900 |
| MAE | 18.67 plates |
| RMSE | 23.10 plates |
| R² Score | 0.837 |
| Baseline MAE | 47.40 plates |

### Meaning of Evaluation Metrics

**MAE (Mean Absolute Error)**

It calculates the average absolute difference between actual and predicted values.

The project's MAE is approximately 18.67 plates.

**RMSE (Root Mean Squared Error)**

It measures prediction error and gives more importance to larger errors.

The project's RMSE is approximately 23.10 plates.

**R² Score (Coefficient of Determination)**

It indicates how well the model explains variations in the target values.

The project's R² score is 0.837.

**Baseline MAE**

A baseline is a simple reference used to compare model performance. Here, the model's MAE is compared with a simple prediction based on the training mean.

**Note:** These results describe performance on the synthetic demonstration dataset. An R² score of 0.837 does not mean 83.7% prediction accuracy on real canteen demand.

## 8. MongoDB Configuration

MessMind uses MongoDB as its database and PyMongo as the Python driver.

You can use either:

- MongoDB Atlas (cloud database)
- Local MongoDB server

### Configure environment variables

1. Open the `backend` folder.
2. Copy `.env.example` and create a new file named `.env`.
3. Add your MongoDB connection details.

Example:

```env
MONGODB_URI=mongodb+srv://USERNAME:PASSWORD@YOUR-CLUSTER.mongodb.net/?retryWrites=true&w=majority
MONGODB_DATABASE=messmind
```

Replace the example values with your actual MongoDB connection details.

Do not upload or share your `.env` file because it contains private database credentials.

If your password contains special characters, URL-encode them in the connection URI.

### MongoDB Collections

The project uses two main collections:

| Collection | Purpose |
|---|---|
| `training_data` | Stores the imported dataset records |
| `demand_records` | Stores prediction inputs, predicted demand and timestamps |

### PyMongo Operations

- `insert_many()` — Imports multiple dataset records into MongoDB.
- `insert_one()` — Stores an individual prediction record.
- `find()` — Retrieves records, including recent prediction history.

MongoDB stores and retrieves information. Model training and regression predictions are performed in Python using Scikit-learn.

## 9. Import Dataset into MongoDB

Run this command from the `backend` folder:

```powershell
python seed_database.py
```

This script imports the CSV dataset into the `training_data` collection.

The prediction history is stored separately in the `demand_records` collection when predictions are successfully saved by the application.

## 10. Start the Backend Server

Make sure you are inside the `backend` folder.

Run:

```powershell
python -m uvicorn app:app --reload
```

After the server starts, open:

**Application API:** http://127.0.0.1:8000

**API Documentation:** http://127.0.0.1:8000/docs

The API documentation allows you to view and test the available backend endpoints.

### Main API Endpoints

| Endpoint | Method | Purpose |
|---|---|---|
| `/api/health` | GET | Checks application health |
| `/api/metrics` | GET | Retrieves model evaluation metrics |
| `/api/predict` | POST | Generates a demand prediction |
| `/api/history` | GET | Retrieves recent prediction history |

## 11. Run the Frontend

The frontend is located in the `frontend` folder.

You can open `index.html` directly in a browser.

If the browser blocks API requests from a local file, open another terminal from the project root and run:

```powershell
python -m http.server 5500 --directory frontend
```

Then open:

http://127.0.0.1:5500

Make sure the FastAPI backend is running at the same time.

## 12. Application Workflow

The complete application follows these steps:

1. The user opens the MessMind frontend.
2. The user selects the day, meal, food item, weather and campus event.
3. The frontend sends the selected information to the FastAPI backend.
4. The backend passes the input to the trained Random Forest model.
5. The model predicts the estimated number of plates.
6. The backend attempts to save the prediction in MongoDB.
7. The prediction result is returned and displayed on the frontend.
8. Previous prediction records can be retrieved from MongoDB and displayed in the history section.

## 13. Limitations

- The dataset contains synthetic demonstration records, not real canteen sales.
- The evaluation metrics describe performance only on the generated dataset.
- Predictions may differ from actual demand in real-world conditions.
- The model's performance depends on the quality and variety of training data.
- Real historical canteen data is required to evaluate practical usefulness.

## 14. Future Scope

The project can be improved in several ways:

- Collect actual daily canteen sales records.
- Train the model using real historical demand.
- Add more features such as holidays, student attendance and special offers.
- Compare Random Forest with other regression algorithms.
- Retrain the model regularly as new data becomes available.
- Deploy the application for multiple campus canteens.
- Add dashboards showing daily, weekly and monthly demand trends.

## 15. Conclusion

MessMind demonstrates how Python, MongoDB and Machine Learning can be combined to build a simple demand prediction application.

It uses Random Forest Regression to estimate the number of plates based on selected inputs.

The project also demonstrates dataset handling, model training, testing, evaluation, API development and database integration.

It provides a foundation for a more practical canteen demand forecasting system using real-world data.