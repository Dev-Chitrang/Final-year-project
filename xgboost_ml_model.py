import pandas as pd
import xgboost as xgb
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

# Load dataset
df = pd.read_excel('balanced_data.xlsx')
print(df.head())
# df.drop(columns=['labels', '2014Q4'], inplace=True)

print(df['labels'].value_counts())

X = df.drop('labels', axis=1)
y = df['labels']

# Split data
# X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Define model
xgb_model = xgb.XGBClassifier(
    n_estimators=500,
    max_depth=8,
    learning_rate=0.03,
    min_child_weight=3,
    gamma=0.2,
    subsample=0.85,
    colsample_bytree=0.85,
    reg_lambda=2,
    reg_alpha=0.1,
    random_state=42,
    tree_method='hist'
)

xgb_model.fit(X, y)

# y_pred = xgb_model.predict(X_test)
# # Evaluate model
# accuracy = accuracy_score(y_test, y_pred)
# precision = precision_score(y_test, y_pred, average='macro')
# recall = recall_score(y_test, y_pred, average='macro')
# f1 = f1_score(y_test, y_pred, average='macro')

# print(f"Accuracy: {accuracy:.2f}")
# print(f"Precision: {precision:.2f}")
# print(f"Recall: {recall:.2f}")
# print(f"F1 Score: {f1:.2f}")

# skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
# scores = cross_val_score(xgb_model, X, y, cv=skf, scoring='accuracy')
# print("Cross-validation Accuracy:", scores.mean())

# # Feature Importance Plot
# xgb.plot_importance(xgb_model)
# plt.show()

xgb_model.save_model('xgboost_model.json')
