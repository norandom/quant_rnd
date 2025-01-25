import nest_asyncio
nest_asyncio.apply()

from llama_index.core import SimpleDirectoryReader
import os

def save_as_markdown(documents, output_path):
    """Save document content as markdown"""
    with open(output_path, 'w', encoding='utf-8') as f:
        for doc in documents:
            # Write metadata as YAML front matter
            f.write('---\n')
            if hasattr(doc, 'metadata') and doc.metadata:
                for key, value in doc.metadata.items():
                    f.write(f'{key}: {value}\n')
            f.write('---\n\n')
            # Write content
            f.write(doc.text)
            f.write('\n\n')

# For demonstration, let's use SimpleDirectoryReader instead of LlamaParse
# since LlamaParse requires an API key
def process_documents(file_path: str):
    reader = SimpleDirectoryReader(input_files=[file_path])
    documents = reader.load_data()
    
    # Save as markdown
    markdown_path = os.path.splitext(file_path)[0] + '.md'
    save_as_markdown(documents, markdown_path)
    print(f"Saved markdown version to: {markdown_path}")
    
    return documents

# Example usage
if __name__ == "__main__":
    
    # Handle complex Excel file
    excel_path = os.path.join(current_dir, "BASF_Case_Study_Modul1.xlsx")
    if os.path.exists(excel_path):
        excel_documents = process_documents(excel_path)
        
    else:
        print(f"No Excel file found at {pdf_path}")
  