import json
import os

# Content from PROMPT 8 (The EDA Notebook Structure)
notebook_content = {
 "cells": [
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "# RECOV.AI - Exploratory Data Analysis\n",
    "\n",
    "## Analyzing Training Data for Debt Recovery Prediction Model\n",
    "\n",
    "**Objective:** Understand data quality, distributions, correlations, and patterns before model training.\n",
    "\n",
    "**Key Focus:** Relationship between **shipping data** and **payment outcome**\n",
    "\n",
    "---"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "import pandas as pd\n",
    "import numpy as np\n",
    "import matplotlib.pyplot as plt\n",
    "import seaborn as sns\n",
    "%matplotlib inline\n",
    "\n",
    "# Set style\n",
    "sns.set_style(\"whitegrid\")\n",
    "plt.rcParams['figure.figsize'] = (12, 6)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Load training data\n",
    "try:\n",
    "    df = pd.read_csv('../../backend/data/training_data.csv')\n",
    "except:\n",
    "    df = pd.read_csv('../backend/data/training_data.csv')\n",
    "\n",
    "# Display first 10 rows\n",
    "df.head(10)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Summary statistics\n",
    "df.describe()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Outcome Distribution\n",
    "sns.countplot(x='outcome', data=df)\n",
    "plt.title('Distribution of Payment Outcomes')\n",
    "plt.show()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "# KEY ANALYSIS: Shipping vs Outcome\n",
    "sns.boxplot(x='outcome', y='shipment_volume_change_30d', data=df)\n",
    "plt.title('Shipment Volume Change vs Payment Outcome')\n",
    "plt.show()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Correlation Heatmap\n",
    "plt.figure(figsize=(10,8))\n",
    "sns.heatmap(df.corr(), annot=True, cmap='coolwarm')\n",
    "plt.title('Feature Correlation Matrix')\n",
    "plt.show()"
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.8.5"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 4
}

# Ensure directory exists
os.makedirs('ml/notebooks', exist_ok=True)

# Write file
file_path = 'ml/notebooks/01_exploratory_data_analysis.ipynb'
with open(file_path, 'w') as f:
    json.dump(notebook_content, f, indent=2)

print(f"✅ Notebook successfully created at: {file_path}")