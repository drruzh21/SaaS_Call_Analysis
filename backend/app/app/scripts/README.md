# Scripts

This directory contains utility scripts for the application.

## Generate Test Data

The `generate_test_data.py` script creates test data for the call analysis system. It generates:
- 150 call analysis results for company ID 1 (using 5 predefined manager names)
- 150 call analysis results for company ID 5 (using 5 predefined manager names)
- 10 common objections
- Random associations between calls and objections

### Features
- Each company has 5 fixed manager names that are used randomly
- Metric values are strictly 0.0, 0.5, or 1.0
- All dates are set to December 2024
- Each call has 1-3 random objections associated with it

### Running the Script

There are two ways to run the script:

1. Inside Docker container (recommended):
```bash
docker exec -it saas-call-analyzer-backend-1 python app/scripts/generate_test_data.py
```

2. Locally (make sure you have the correct database connection):
```bash
cd backend/app
python app/scripts/generate_test_data.py
```

### Notes

- The script is idempotent - running it multiple times will add new data each time
- All dates are in December 2024
- Each call has 1-3 random objections associated with it
