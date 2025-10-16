"""Document processing for cluster files

This module handles:
- Loading cluster documents from the clusters/ folder
- Parsing project codes, titles, and descriptions
- Extracting structured project information
- PDF support for Horizon Europe work programme documents
"""

import os
from pathlib import Path
from typing import Dict, List, Optional
import re

# PDF processing
try:
    from pypdf import PdfReader
    PDF_SUPPORT = True
except ImportError:
    try:
        from PyPDF2 import PdfReader
        PDF_SUPPORT = True
    except ImportError:
        PDF_SUPPORT = False
        print("PDF support not available. Install with: pip install pypdf")


class ClusterProject:
    """Represents a single project within a cluster document"""
    
    def __init__(self, code: str, title: str, description: str, cluster_name: str):
        self.code = code
        self.title = title
        self.description = description
        self.cluster_name = cluster_name
        self.full_text = f"{code}\n{title}\n{description}"
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'code': self.code,
            'title': self.title,
            'description': self.description,
            'cluster': self.cluster_name,
            'full_text': self.full_text
        }


class ClusterDocument:
    """Represents a cluster document containing multiple projects"""
    
    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.cluster_name = file_path.stem
        self.content = self._load_content()
        self.projects: List[ClusterProject] = self._extract_projects()
    
    def _load_content(self) -> str:
        """Load document content from various formats"""
        file_extension = self.file_path.suffix.lower()
        
        if file_extension == '.pdf':
            return self._load_pdf()
        else:
            return self._load_text_file()
    
    def _load_text_file(self) -> str:
        """Load content from text files (.txt, .md)"""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            # Try with different encoding
            try:
                with open(self.file_path, 'r', encoding='latin-1') as f:
                    return f.read()
            except Exception as e:
                print(f"   Error loading {self.file_path.name}: {e}")
                return ""
        except Exception as e:
            print(f"   Error loading {self.file_path.name}: {e}")
            return ""
    
    def _load_pdf(self) -> str:
        """Load content from PDF files"""
        if not PDF_SUPPORT:
            print(f"   PDF support not available for {self.file_path.name}")
            return ""
        
        try:
            reader = PdfReader(self.file_path)
            text_content = []
            
            for page_num, page in enumerate(reader.pages, 1):
                try:
                    text = page.extract_text()
                    if text:
                        text_content.append(text)
                except Exception as e:
                    print(f"Error extracting page {page_num}: {e}")
            
            full_text = '\n'.join(text_content)
            print(f"Extracted {len(reader.pages)} pages, {len(full_text)} characters")
            return full_text
            
        except Exception as e:
            print(f"Error reading PDF {self.file_path.name}: {e}")
            return ""
    
    def _extract_projects(self) -> List[ClusterProject]:
        """Extract individual projects from cluster document
        
        Looks for patterns like:
        HORIZON-CL4-2024-DIGITAL-EMERGING-01-01
        Project Title
        Description...
        """
        if not self.content:
            return []
        
        projects = []
        
        # Pattern to match Horizon project codes
        # Matches: HORIZON-XXX-YYYY-...-NN-NN or HORIZON-XXX-YYYY-NN
        project_pattern = r'(HORIZON-[A-Z0-9]+-[0-9]{4}(?:-[0-9]{4})?(?:-[A-Z0-9-]+)*)'
        
        # Find all project codes in the document
        matches = list(re.finditer(project_pattern, self.content))
        
        if not matches:
            print(f"   No HORIZON project codes found in {self.file_path.name}")
            return []
        
        print(f"Found {len(matches)} HORIZON codes")
        
        # Extract content for each project
        for i, match in enumerate(matches):
            project_code = match.group(1).strip()
            start_pos = match.end()
            
            # Determine end position (next project or end of document)
            if i + 1 < len(matches):
                end_pos = matches[i + 1].start()
            else:
                end_pos = len(self.content)
            
            # Extract project content
            project_content = self.content[start_pos:end_pos].strip()
            
            # Extract title and description
            lines = [line.strip() for line in project_content.split('\n') if line.strip()]
            
            if lines:
                # First substantial line is the title
                title = lines[0][:200]  # Limit title length
                
                # Rest is description
                description_lines = []
                for line in lines[1:]:
                    # Stop at certain markers or if too long
                    if len('\n'.join(description_lines)) > 2000:
                        break
                    if line.startswith('HORIZON-'):  # Another project started
                        break
                    description_lines.append(line)
                
                description = '\n'.join(description_lines)
                
                project = ClusterProject(
                    code=project_code,
                    title=title,
                    description=description,
                    cluster_name=self.cluster_name
                )
                projects.append(project)
        
        return projects
    
    def get_project_count(self) -> int:
        """Get number of projects in this document"""
        return len(self.projects)


class ClusterDocumentManager:
    """Manages all cluster documents"""
    
    def __init__(self, clusters_folder: str):
        self.clusters_folder = Path(clusters_folder)
        self.documents: List[ClusterDocument] = []
        self.load_documents()
    
    def load_documents(self):
        """Load all documents from clusters folder"""
        self.documents = []
        
        if not self.clusters_folder.exists():
            print(f"Clusters folder not found: {self.clusters_folder}")
            print(f"Creating clusters folder...")
            self.clusters_folder.mkdir(parents=True, exist_ok=True)
            print(f"Created: {self.clusters_folder}")
            print(f"Add .txt, .md, or .pdf files to this folder")
            return
        
        # Support .txt, .md, and .pdf files
        supported_extensions = ['.txt', '.md', '.pdf']
        files_found = list(self.clusters_folder.glob('*'))
        
        print(f"Scanning: {self.clusters_folder}")
        print(f"Files found: {len(files_found)}")
        
        if not PDF_SUPPORT:
            print(f"PDF support not available. Install with: pip install pypdf")
        
        loaded_count = 0
        for file_path in files_found:
            if file_path.is_file() and file_path.suffix.lower() in supported_extensions:
                print(f" Processing: {file_path.name}")
                
                # Skip PDFs if no support
                if file_path.suffix.lower() == '.pdf' and not PDF_SUPPORT:
                    print(f"   Skipped PDF (install pypdf): {file_path.name}")
                    continue
                
                try:
                    doc = ClusterDocument(file_path)
                    if doc.projects:  # Only add if projects were found
                        self.documents.append(doc)
                        loaded_count += 1
                        print(f"   Loaded: {file_path.name} ({len(doc.projects)} projects)")
                    else:
                        print(f"   No valid projects extracted from: {file_path.name}")
                except Exception as e:
                    print(f"   Error processing {file_path.name}: {e}")
                    import traceback
                    traceback.print_exc()
            elif file_path.is_file():
                print(f" Skipped: {file_path.name} (unsupported format)")
        
        if loaded_count == 0:
            print(f"\nNo valid cluster documents loaded")
            print(f"Add .txt, .md, or .pdf files with HORIZON project codes")
            if not PDF_SUPPORT:
                print(f"For PDF support, run: pip install pypdf")
        else:
            print(f"\nTotal: Loaded {loaded_count} cluster documents")
            total_projects = sum(len(doc.projects) for doc in self.documents)
            print(f"Total projects extracted: {total_projects}")
    
    def get_all_projects(self) -> List[ClusterProject]:
        """Get all projects from all cluster documents"""
        all_projects = []
        for doc in self.documents:
            all_projects.extend(doc.projects)
        return all_projects
    
    def get_project_by_code(self, code: str) -> Optional[ClusterProject]:
        """Find a project by its code"""
        for doc in self.documents:
            for project in doc.projects:
                if project.code.lower() == code.lower():
                    return project
        return None
    
    def search_by_keywords(self, keywords: List[str]) -> List[Dict]:
        """Search for keywords in all cluster projects
        
        Returns list of matches with scores
        """
        results = []
        
        for doc in self.documents:
            for project in doc.projects:
                matched_keywords = []
                text_lower = project.full_text.lower()
                
                for keyword in keywords:
                    if keyword.lower() in text_lower:
                        matched_keywords.append(keyword)
                
                if matched_keywords:
                    results.append({
                        'project': project,
                        'matched_keywords': matched_keywords,
                        'match_count': len(matched_keywords)
                    })
        
        # Sort by match count (highest first)
        results.sort(key=lambda x: x['match_count'], reverse=True)
        return results
    
    def get_statistics(self) -> Dict:
        """Get statistics about loaded cluster documents"""
        all_projects = self.get_all_projects()
        
        stats = {
            'total_documents': len(self.documents),
            'total_projects': len(all_projects),
            'projects_by_cluster': {},
            'document_details': []
        }
        
        for doc in self.documents:
            cluster_name = doc.cluster_name
            project_count = len(doc.projects)
            stats['projects_by_cluster'][cluster_name] = project_count
            stats['document_details'].append({
                'name': cluster_name,
                'file': doc.file_path.name,
                'projects': project_count
            })
        
        return stats