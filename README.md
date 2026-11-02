# MessMind — Campus Canteen Demand Predictor

**CA requirements covered:** Python programming, MongoDB backend through PyMongo, a dataset, one regression algorithm, a 70/30 train-test split, and prediction evaluation on unseen test rows.

MessMind estimates the number of plates likely to be needed for a selected day, meal, menu item, weather condition and campus event. Predictions are saved in MongoDB when a database connection is configured. The interface is intentionally limited to a prediction form, model evaluation summary and recent prediction history.

## Important dataset note

`backend/dataset.csv` contains 3,000 **synthetic demonstration records** generated for this project. It is a valid sample dataset for demonstrating the full programming workflow, but it is not collected from a real college canteen. The reported test metrics therefore show how the model learns the patterns in this generated dataset; they must not be presented as proof of real-world canteen accuracy. If your teacher requires a real-world dataset, replace this CSV with a properly licensed food-demand dataset and adapt the column mapping. A commonly used public reference is the Genpact Food Demand Forecasting dataset, which contains historical meal-order counts and meal/fulfilment-centre information: https://datahack.analyticsvidhya.com/contest/genpact-machine-learning-hackathon-1/ .

## Project structure

```text
MessMind_CA_Project/
├── backend/
│   ├── app.py                 # FastAPI endpoints
│   ├── database.py            # MongoDB connection through PyMongo
│   ├── dataset.csv            # 3,000 sample rows
│   ├── generate_data.py       # Re-create the demonstration dataset
│   ├── model.py               # Load model and make predictions
│   ├── train_model.py         # 70/30 training and testing + evaluation
│   ├── test_predictions.csv   # Actual vs predicted values for held-out test rows
│   ├── model.joblib           # Trained regression pipeline
│   ├── seed_database.py       # Import CSV into MongoDB
│   ├── requirements.txt
│   └── .env.example
└── frontend/
    ├── index.html             # Simple prediction/evaluation UI
    ├── style.css
    └── script.js
```

## 1. Install dependencies (Windows PowerShell)

Open a terminal in the `backend` folder:

```powershell
python -m pip install -r requirements.txt
```

## 2. Configure MongoDB

Create a free MongoDB Atlas cluster or use a local MongoDB server. Copy `.env.example` to `.env` in the `backend` folder and set your connection details:

```env
MONGODB_URI=mongodb+srv://USERNAME:PASSWORD@YOUR-CLUSTER.mongodb.net/?retryWrites=true&w=majority
MONGODB_DATABASE=messmind
```

Replace the placeholders. Do not share or upload your `.env` file. If your password contains special characters, URL-encode them.

## 3. Train and test the regression model

Run from inside `backend`:

```powershell
python train_model.py
```

The code uses **Random Forest Regression**. It separates the 3,000 rows into:

- 1,500 rows (50%) for training the model.
- 1,500 different rows (50%) for testing the model.

The model never sees the test rows during training. It predicts demand for those held-out rows and compares predictions with their known `demand` values. It reports MAE, RMSE and R², compares MAE with a simple mean-prediction baseline, saves the trained pipeline to `model.joblib`, and writes row-by-row actual/predicted values to `test_predictions.csv`.

### Evaluation from the included dataset

A training run during project preparation produced the following illustrative run results (your environment may show small differences if you regenerate the dataset):

| Measure | Result |
|---|---:|
| Total dataset rows | 3,000 |
| Training rows | 1,500 (50%) |
| Testing rows | 1,500 (50%) |
| Test MAE | 18.86 plates |
| Test RMSE | 23.36 plates |
| Test R² | 0.835 |
| Baseline MAE | 47.78 plates |

**Interpretation:** On this held-out synthetic test set, the model's predictions differed from actual generated demand by about 18.86 plates on average (MAE). The R² value indicates fit to this synthetic dataset only. It does not guarantee the same performance on real canteen data.

## 4. Import the dataset into MongoDB

```powershell
python seed_database.py
```

This imports the CSV into the `training_data` collection once. The application stores generated predictions in `demand_records`. MongoDB is used as the persistent backend; model training and prediction are performed in Python using scikit-learn.

## 5. Start the backend

Still inside `backend`:

```powershell
python -m uvicorn app:app --reload
```

API documentation: http://127.0.0.1:8000/docs

## 6. Open the frontend

Open `frontend/index.html` in your browser. If the browser blocks API calls from a local file, open a second terminal from the project root and run:

```powershell
python -m http.server 5500 --directory frontend
```

Then visit http://127.0.0.1:5500 .

## MongoDB collections and Python operations

- `training_data`: the imported dataset (3,000 documents).
- `demand_records`: prediction inputs, predicted plate counts and timestamps.
- PyMongo `insert_many()` imports the dataset; `insert_one()` stores predictions; `find()` retrieves recent prediction history.

## Algorithm details

- Input features: `day`, `meal`, `item`, `weather`, `event`.
- Target: `demand` (numeric number of plates), so this is a regression problem.
- Categorical features are one-hot encoded.
- Algorithm: `RandomForestRegressor` from scikit-learn.
- Split: `train_test_split(test_size=0.5, random_state=42)`.
- Evaluation: MAE, RMSE and R² on the unseen 30% test data.

## Suggested viva explanation

1. **Why regression?** The output is a numeric quantity: the number of plates demanded.
2. **What is the dataset?** A 3,000-row sample CSV containing day, meal, item, weather, event and demand. It is synthetic demonstration data.
3. **How did you split it?** 50% for training and 50% for testing.
4. **How do you check predictions?** Compare predicted demand with actual `demand` values in the held-out test set and calculate MAE, RMSE and R².
5. **What is PyMongo?** The Python driver used to connect Python code to MongoDB and perform database operations.
6. **What does MongoDB store?** The imported dataset and prediction history.
7. **Where is regression performed?** In Python using scikit-learn; MongoDB stores and retrieves the data.

## Limitations

- The included dataset is synthetic, not measured canteen data.
- Test metrics describe performance on the generated dataset only.
- Real-world accuracy must be checked with genuine historical canteen sales.
- Keep database credentials in `backend/.env`; never commit or share that file.
