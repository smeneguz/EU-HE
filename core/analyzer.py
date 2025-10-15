"""Core analysis logic"""

import pandas as pd
from typing import List, Dict, Tuple
from pathlib import Path

from .models import ProjectMatch
from config.keywords import (
    BLOCKCHAIN_KEYWORDS,
    PRIVACY_KEYWORDS,
    DATA_GOVERNANCE_KEYWORDS,
    AI_KEYWORDS,
    IOT_KEYWORDS,
    WEIGHTS,
    MIN_SCORE_THRESHOLD
)


class ProjectAnalyzer:
    """Analyzes Excel files for project matching"""
    
    def __init__(self, excel_path: str):
        self.excel_path = Path(excel_path)
        self.matches: List[ProjectMatch] = []
    
    def load_excel(self) -> Dict[str, pd.DataFrame]:
        """Load all sheets from Excel file"""
        excel_file = pd.ExcelFile(self.excel_path)
        sheets = {}
        
        for sheet_name in excel_file.sheet_names:
            # Read Excel with header detection
            df = pd.read_excel(self.excel_path, sheet_name=sheet_name)
            sheets[sheet_name] = df
        
        return sheets
    
    def calculate_score(self, text: str) -> Tuple[int, Dict[str, List[str]], List[str]]:
        """Calculate match score and identify keywords"""
        if pd.isna(text):
            return 0, {}, []
        
        text_lower = str(text).lower()
        score = 0
        matched_keywords = {}
        technologies = []
        
        blockchain_matches = [kw for kw in BLOCKCHAIN_KEYWORDS if kw in text_lower]
        if blockchain_matches:
            score += len(blockchain_matches) * WEIGHTS['blockchain']
            matched_keywords['blockchain'] = blockchain_matches
            technologies.append('Blockchain/DLT')
        
        privacy_matches = [kw for kw in PRIVACY_KEYWORDS if kw in text_lower]
        if privacy_matches:
            score += len(privacy_matches) * WEIGHTS['privacy']
            matched_keywords['privacy'] = privacy_matches
            technologies.append('Privacy-Preserving')
        
        data_matches = [kw for kw in DATA_GOVERNANCE_KEYWORDS if kw in text_lower]
        if data_matches:
            score += len(data_matches) * WEIGHTS['data_governance']
            matched_keywords['data_governance'] = data_matches
            technologies.append('Data Governance')
        
        ai_matches = [kw for kw in AI_KEYWORDS if kw in text_lower]
        if ai_matches:
            score += len(ai_matches) * WEIGHTS['ai']
            matched_keywords['ai'] = ai_matches
            technologies.append('AI/ML')
        
        iot_matches = [kw for kw in IOT_KEYWORDS if kw in text_lower]
        if iot_matches:
            score += len(iot_matches) * WEIGHTS['iot']
            matched_keywords['iot'] = iot_matches
            technologies.append('IoT')
        
        return score, matched_keywords, technologies
    
    def determine_roles(self, score: int) -> List[str]:
        """Determine potential roles based on score"""
        from config.keywords import HIGH_PRIORITY_THRESHOLD, MEDIUM_PRIORITY_THRESHOLD
        
        if score >= HIGH_PRIORITY_THRESHOLD:
            return ['Technical Coordinator', 'WP Leader - Technology']
        elif score >= MEDIUM_PRIORITY_THRESHOLD:
            return ['WP Leader', 'Task Leader']
        else:
            return ['Task Leader', 'Partner']
    
    def suggest_contributions(self, technologies: List[str], matched_keywords: Dict) -> List[str]:
        """Suggest specific contributions"""
        contributions = []
        
        if 'Blockchain/DLT' in technologies:
            contributions.extend([
                'Blockchain infrastructure and smart contracts',
                'Decentralized trust mechanisms',
                'Immutable audit trails'
            ])
        
        if 'Privacy-Preserving' in technologies:
            if 'zk' in str(matched_keywords.get('privacy', [])).lower():
                contributions.append('Zero-knowledge proof implementation')
            if 'tee' in str(matched_keywords.get('privacy', [])).lower():
                contributions.append('Trusted Execution Environment integration')
            contributions.append('Privacy-preserving protocols')
        
        if 'Data Governance' in technologies:
            contributions.extend([
                'Data sovereignty frameworks',
                'Access control mechanisms',
                'Compliance and audit systems'
            ])
        
        if 'AI/ML' in technologies:
            contributions.extend([
                'Federated learning infrastructure',
                'Privacy-preserving AI training'
            ])
        
        return contributions
    
    def analyze_sheet(self, sheet_name: str, df: pd.DataFrame) -> List[ProjectMatch]:
        """Analyze a single sheet"""
        matches = []
        
        # The DataFrame index already corresponds to the actual row number in Excel
        # df.index starts from 0, but Excel rows start from 1
        # If there's a header row, pandas automatically uses it and starts data from index 0
        # We need to add 2 to account for: 1-based indexing + header row
        
        for idx, row in df.iterrows():
            combined_text = ' '.join([
                str(row.get(col, ''))
                for col in df.columns
                if pd.notna(row.get(col, ''))
            ])
            
            score, matched_keywords, technologies = self.calculate_score(combined_text)
            
            if score >= MIN_SCORE_THRESHOLD:
                # Excel row = pandas index + 2 (1 for Excel 1-based indexing, 1 for header)
                excel_row = idx + 2
                
                match = ProjectMatch(
                    row_index=excel_row,  # This is now the actual Excel row number
                    sheet_name=sheet_name,
                    score=score,
                    matched_keywords=matched_keywords,
                    technologies=technologies,
                    potential_roles=self.determine_roles(score),
                    contributions=self.suggest_contributions(technologies, matched_keywords),
                    project_data=row.to_dict()
                )
                matches.append(match)
        
        return matches
    
    def analyze_all(self) -> List[ProjectMatch]:
        """Analyze all sheets"""
        sheets = self.load_excel()
        self.matches = []
        
        for sheet_name, df in sheets.items():
            sheet_matches = self.analyze_sheet(sheet_name, df)
            self.matches.extend(sheet_matches)
        
        self.matches.sort(key=lambda x: x.score, reverse=True)
        return self.matches