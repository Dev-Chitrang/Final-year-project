import pandas as pd
from sklearn.preprocessing import LabelEncoder, StandardScaler
from imblearn.over_sampling import RandomOverSampler, SMOTE
import xgboost as xgb
import joblib


# Load Data
df = pd.read_excel('updated_final_data.xlsx')

# Drop Irrelevant Columns
df.drop(columns=['labels', 'Investment_Class'], inplace=True)
df.dropna(inplace=True)

# Encode Target Column
label_encoder = LabelEncoder()
df['target'] = label_encoder.fit_transform(df['2014Q4'])
df.drop(columns=['2014Q4'], inplace=True)

# Features & Target
X = df.drop(columns=['target'])
y = df['target']


# Handle Imbalanced Data with RandomOverSampler (First Step)
ros = RandomOverSampler(sampling_strategy='not majority', random_state=42)
X_resampled, y_resampled = ros.fit_resample(X, y)

# Apply SMOTE to Further Balance the Dataset
smote = SMOTE(sampling_strategy="auto", random_state=42, k_neighbors=3)
X_final, y_final = smote.fit_resample(X_resampled, y_resampled)

# Define XGBoost Model for Full Dataset Training
xgb_clf = xgb.XGBClassifier(
    objective='multi:softmax',
    num_class=len(label_encoder.classes_),
    eval_metric='mlogloss',
    learning_rate=0.03,
    max_depth=7,
    n_estimators=1000,
    subsample=0.85,
    colsample_bytree=0.85,
    min_child_weight=2,
    gamma=0.3,
    random_state=42
)

# Train the Model on Entire Dataset
xgb_clf.fit(X_final, y_final, verbose=100)

# Save the trained model
xgb_clf.save_model('new_xgboost_model.json')
joblib.dump(label_encoder, "label_encoder.pkl")