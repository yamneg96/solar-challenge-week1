# Solar Data Challenge - Week 0

## Project Overview

Analysis of solar farm data from Benin, Sierra Leone, and Togo to identify high-potential regions for solar investment.

## Setup Instructions

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Lemiti/solar-challenge-week1.git
   cd solar-challenge-week1
   ```
2. **Set up a virtual environment**:

   ```bash
   python -m venv .venv
   source .venv/bin/activate # Linux/Mac
   .venv\Script\activate #Windows
   pip install -r requirements.tx
   ```

3. **Run CI checks locally**
   ```bash
   act -j test # Requires GitHub Actions CLI (optional)
   ```

## Folder Structure

```
solar-challenge-week1/
├── .github/
│   └── workflows/
│       └── ci.yml
├── .gitignore
├── requirements.txt
├── README.md
|------ src/
├── notebooks/
│   ├── __init__.py
│   └── README.md
├── tests/
│   ├── __init__.py
└── scripts/
    ├── __init__.py
    └── README.md
```
