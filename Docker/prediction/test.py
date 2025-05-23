import pickle
import numpy as np

with open("xgb_block_model_v2.pkl", "rb") as f:
    model = pickle.load(f)

import matplotlib.pyplot as plt

plt.bar(range(len(model.feature_importances_)), model.feature_importances_)
plt.title("Feature Importances")
plt.xlabel("Feature Index")
plt.ylabel("Importance")
plt.show()
