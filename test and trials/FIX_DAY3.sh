#!/bin/bash

echo "🔧 RECOV.AI - Day 3 Complete Fix Script"
echo "========================================"

# Backup current files
echo "📦 Creating backups..."
cp backend/predictor.py backend/predictor. py.backup
cp backend/main.py backend/main.py. backup
cp backend/models.py backend/models.py.backup
cp test_api.py test_api. py.backup
cp backend/data/demo_data. csv backend/data/demo_data.csv.backup

echo "✅ Backups created with . backup extension"

# You need to manually replace the files with the code above
echo ""
echo "📝 NEXT STEPS:"
echo "1. Replace backend/predictor.py with PACKAGE 1"
echo "2. Replace backend/main.py with PACKAGE 2"
echo "3. Replace backend/models.py with PACKAGE 3"
echo "4. Replace test_api.py with PACKAGE 4"
echo "5. Replace backend/data/demo_data.csv with PACKAGE 5"
echo ""
echo "Then run:"
echo "  cd backend"
echo "  python -m uvicorn main:app --reload"
echo ""
echo "In another terminal:"
echo "  python test_api.py"