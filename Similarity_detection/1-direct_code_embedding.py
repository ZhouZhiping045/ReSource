import os
import csv
import torch
from transformers import AutoTokenizer, AutoModel
import numpy as np
import glob
import re
from collections import defaultdict, Counter
import uuid

# Initialize device
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"Using device: {device}")

# Load fine-tuned CodeBERT model and tokenizer
FINETUNED_MODEL_PATH = "microsoft/graphcodebert-base"
tokenizer = AutoTokenizer.from_pretrained(FINETUNED_MODEL_PATH)
model = AutoModel.from_pretrained(FINETUNED_MODEL_PATH)
model.to(device)

class SimpleCodeFolder:
    """Simple code folder with no_folding method only"""

    def __init__(self, tokenizer, max_tokens=512):
        self.tokenizer = tokenizer
        self.max_tokens = max_tokens

    def fold_code(self, code):
        """Main code folding interface - uses no_folding method"""
        try:
            return self._no_folding(code)
        except Exception as e:
            print(f"  Error in fold_code: {e}, falling back to truncation")
            tokens = self.tokenizer.tokenize(code)[:self.max_tokens]
            return self.tokenizer.convert_tokens_to_string(tokens)

    def _no_folding(self, code):
        """No folding, directly return original code or truncate if too long"""
        tokens = self.tokenizer.tokenize(code)
        if len(tokens) > self.max_tokens:
            print(f"  No_folding exceeds max_tokens ({len(tokens)} > {self.max_tokens}), truncating...")
            return self.tokenizer.convert_tokens_to_string(tokens[:self.max_tokens])
        return code

# Initialize folder
code_folder = SimpleCodeFolder(tokenizer, max_tokens=512)

def fold_code(code, tokenizer=None, max_tokens=512):
    """Fold code function"""
    return code_folder.fold_code(code)

def generate_code_embedding(folded_code):
    """Generate code embedding, ensure 1D output"""
    if not folded_code or not folded_code.strip():
        print("  Warning: Empty folded code, returning zero embedding")
        return np.zeros(768)
    try:
        inputs = tokenizer(folded_code, return_tensors="pt", truncation=True, padding=True, max_length=512)
        inputs = {k: v.to(device) for k, v in inputs.items()}
        with torch.no_grad():
            outputs = model(**inputs)
        # Flatten to 1D vector
        embedding = outputs.last_hidden_state[:, 0, :].cpu().numpy().ravel()
        if embedding.shape != (768,):
            print(f"  Warning: Embedding shape {embedding.shape}, reshaping to (768,)")
            embedding = embedding.reshape(768)
        return embedding
    except Exception as e:
        print(f"  Error generating embedding: {e}, returning zero embedding")
        return np.zeros(768)

def preprocess_csv(file_path):
    """Preprocess CSV file"""
    for encoding in ['utf-8', 'latin-1', 'cp1252']:
        try:
            with open(file_path, 'r', encoding=encoding) as csvfile:
                reader = csv.reader(csvfile)
                next(reader, None)  # Skip header
                rows = [{"id": row[0].strip(), "function_name": row[1].strip(), "code": row[2].replace('\\n', '\n').replace('\\t', '\t')}
                        for row in reader if len(row) == 3]
                print(f"Preprocessed {len(rows)} functions from {file_path} using {encoding} encoding.")
                return rows
        except UnicodeDecodeError:
            continue
    print(f"Error: Could not decode {file_path}.")
    return []

def process_function(row):
    """Process single function"""
    function_name, code = row['function_name'], row['code']
    print(f"Processing function: {function_name}")

    original_tokens = len(tokenizer.tokenize(code))
    if original_tokens > 512:
        print(f"  Original code: {original_tokens} tokens > 512, applying folding...")

    try:
        folded_code = fold_code(code)
        embedding = generate_code_embedding(folded_code)
        folded_tokens = len(tokenizer.tokenize(folded_code))
        print(f"  Folded to: {folded_tokens} tokens")
        if original_tokens > 512:
            print(f"  Token reduction: {(original_tokens - folded_tokens) / original_tokens * 100:.1f}%")
    except Exception as e:
        print(f"  Error processing {function_name}: {e}, returning zero embedding")
        folded_tokens = 0
        embedding = np.zeros(768)

    return function_name, embedding

def get_csv_files(folder):
    """Get all CSV files from folder"""
    return glob.glob(os.path.join(folder, '*.csv'))

def main():
    print(f"=== Code Embedding Script ===")
    csv_folder = '1_original_csv_fine_grain'
    output_folder = '3_embedding_npy_fine_grain'
    os.makedirs(output_folder, exist_ok=True)

    for csv_file in get_csv_files(csv_folder):
        print(f"\nProcessing CSV file: {csv_file}")
        rows = preprocess_csv(csv_file)
        embeddings = {name: emb for name, emb in (process_function(row) for row in rows)}
        npy_path = os.path.join(output_folder, os.path.basename(csv_file).replace('.csv', '_embeddings.npy'))
        np.save(npy_path, embeddings)
        print(f"Embeddings saved to {npy_path}")

    print("\nAll CSV files processed.")

if __name__ == '__main__':
    main()