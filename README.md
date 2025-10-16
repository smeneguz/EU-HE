# Horizon Europe Project Analyzer
Initial draft of a keyword-based matching tool for European Projects.


```bash
# Clone or download the project
cd proposals_aioti

# Install dependencies
pip install -r requirements.txt
```

## Usage

### 1. Run the Application

```bash
streamlit run app.py
```

### 2. Upload Excel File

- Click "Choose your Horizon Europe Excel file"
- Upload your `.xlsx` or `.xls` file
- Click " Analyze Projects"

### 3. Add Cluster Documents (Optional)

- Place `.txt` or `.md` files in the `clusters/` folder
- Click "Load/Reload Clusters" in sidebar

### 4. Explore Results

- **Excel Analysis Tab**: View matched projects with filtering
- **Cluster Documents Tab**: Search and browse cluster projects
- Enable "Show cluster matches" to see connections

### 5. Export Data

- Download filtered or all results
- CSV for spreadsheet analysis
- JSON for programmatic use

##  Configuration

### Keywords

Edit `config/keywords.py` to customize:
- Technology keywords (blockchain, privacy, AI, etc.)
- Scoring weights
- Priority thresholds


## Scoring System

- **High Priority** (Score >= 9): Coordinator/Tech Lead potential
- **Medium Priority** (Score 6-8): WP/Task Leader potential
- **Low Priority** (Score 3-5): Partner potential

Scoring factors:
- Blockchain/DLT keywords: 3 points each
- Privacy keywords: 3 points each
- Data Governance: 2 points each
- AI/ML: 2 points each
- IoT: 2 points each

## Cluster Matching

Cluster matching scores:
- **Exact code match**: +20 points
- **Each keyword match**: +2 points

Color coding:
- 🟢 High match (score >= 20)
- 🟡 Medium match (score >= 10)
- 🔵 Low match (score < 10)

## Contributing

Follow the modular architecture:
1. Core logic → `core/`
2. UI components → `ui/`
3. Utilities → `utils/`
4. Configuration → `config/`
