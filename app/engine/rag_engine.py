import os
from pathlib import Path
from pypdf import PdfReader

_documents_cache = None

def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extrait le texte d'un fichier PDF
    """
    try:
        text = ""
        reader = PdfReader(pdf_path)
        
        for page_num in range(len(reader.pages)):
            page = reader.pages[page_num]
            text += page.extract_text()
        
        return text
    except Exception as e:
        print(f"[RAG] ERROR extracting PDF {pdf_path}: {str(e)}")
        return ""

def load_documents():
    """Charge tous les documents PDF depuis data/documents"""
    global _documents_cache
    
    if _documents_cache:
        return _documents_cache
    
    try:
        doc_path = Path("./data/documents")
        _documents_cache = {}
        
        # Charge tous les fichiers .pdf
        for pdf_file in sorted(doc_path.glob("*.pdf")):
            text_content = extract_text_from_pdf(str(pdf_file))
            if text_content:
                _documents_cache[pdf_file.name] = text_content
                print(f"[RAG] Loaded PDF: {pdf_file.name}")
            else:
                print(f"[RAG] WARNING - Empty PDF: {pdf_file.name}")
        
        if _documents_cache:
            print(f"[RAG] OK - {len(_documents_cache)} documents PDF loaded")
            return _documents_cache
        else:
            print(f"[RAG] WARNING - No PDF files found in {doc_path}")
            return None
            
    except Exception as e:
        print(f"[RAG] ERROR loading documents: {str(e)}")
        return None

def build_or_load_index():
    """Build a simple index (load documents)"""
    return load_documents()

def query_rag(question: str, machine_id: str = "M1") -> str:
    """
    Recherche simple par mots-clés dans les documents PDF
    
    Algorithme:
    1. Charge les documents PDF si pas en cache
    2. Cherche d'abord procedure_{machine_id}.pdf (priorité haute)
    3. Extrait les lignes contenant les keywords
    4. Fallback: documents généraux (iso_standards.pdf)
    """
    try:
        docs = load_documents()
        if not docs:
            return "Procedure: Stop machine if T > 100C"
        
        # 1️⃣ Cherche le doc spécifique à la machine (PDF)
        machine_doc_name = f"procedure_{machine_id}.pdf"
        if machine_doc_name in docs:
            machine_doc = docs[machine_doc_name]
            print(f"[RAG] Found machine-specific PDF: {machine_doc_name}")
            
            # 2️⃣ Cherche les mots-clés dans ce doc
            keywords = question.lower().split()
            lines = machine_doc.split('\n')
            relevant = []
            
            for line in lines:
                line_lower = line.lower()
                if any(kw in line_lower for kw in keywords) and line.strip() and len(line.strip()) > 10:
                    relevant.append(line.strip())
            
            if relevant:
                # 3️⃣ Retourne les top 5 lignes pertinentes
                result = "\n".join(relevant[:5])
                print(f"[RAG] Found {len(relevant)} relevant lines in {machine_doc_name}")
                return result
            else:
                # Fallback: retourne le début du document
                first_section = machine_doc.split('\n\n')[0]
                print(f"[RAG] No exact match in {machine_doc_name}, returning intro")
                return first_section[:500]
        
        # 4️⃣ Si pas de doc spécifique, cherche dans les docs généraux (iso_standards.pdf)
        keywords = question.lower().split()
        best_doc = None
        best_score = 0
        best_name = None
        
        for doc_name, content in docs.items():
            content_lower = content.lower()
            score = sum(1 for kw in keywords if kw in content_lower)
            
            if score > best_score:
                best_score = score
                best_doc = content
                best_name = doc_name
        
        if best_doc and best_score > 0:
            lines = best_doc.split('\n')
            relevant = []
            
            for line in lines:
                line_lower = line.lower()
                if any(kw in line_lower for kw in keywords) and line.strip() and len(line.strip()) > 10:
                    relevant.append(line.strip())
            
            if relevant:
                result = "\n".join(relevant[:5])
                print(f"[RAG] Found {len(relevant)} relevant lines in {best_name}")
                return result
        
        if best_doc:
            first_section = best_doc.split('\n\n')[0]
            print(f"[RAG] No exact match, returning intro from {best_name}")
            return first_section[:500]
        
        return "Procedure: Stop machine if T > 100C"
        
    except Exception as e:
        print(f"[RAG] ERROR query: {str(e)}")
        return "Procedure: Stop machine if T > 100C"

if __name__ == "__main__":
    print("\n" + "="*70)
    print("🔍 TEST RAG ENGINE - PDF Support")
    print("="*70 + "\n")
    
    # Test 1: Charge les documents
    print("📚 Loading PDF documents...")
    docs = build_or_load_index()
    
    if docs:
        print(f"\n✅ Documents loaded: {list(docs.keys())}\n")
        
        # Test 2: Query pour M1
        print("Test 1: Machine M1 - Question température")
        resp1 = query_rag("emergency procedure for overheating M1", machine_id="M1")
        print(f"Response:\n{resp1[:200]}...\n")
        
        # Test 3: Query pour M2
        print("Test 2: Machine M2 - Question vibration")
        resp2 = query_rag("vibration anomaly procedure", machine_id="M2")
        print(f"Response:\n{resp2[:200]}...\n")
        
        # Test 4: Query pour M3
        print("Test 3: Machine M3 - Question température")
        resp3 = query_rag("high temperature alert", machine_id="M3")
        print(f"Response:\n{resp3[:200]}...\n")
    else:
        print("❌ No documents loaded")
    
    print("="*70)