# Data Directory

This directory contains dataset files and training data for the RAG system.

## 📁 Directory Structure

- **raw/** - Original, unprocessed datasets
  - PDF files, documents, text files
  - Source data before any processing
  - Keep original files here for reproducibility

- **processed/** - Processed and cleaned data
  - Chunked content ready for embedding
  - Vector embeddings
  - Index files for fast retrieval

## 📋 Usage Guidelines

### Adding New Data
1. Place raw files in `data/raw/`
2. Run processing pipeline: `make process-data`
3. Processed files will appear in `data/processed/`

### File Formats Supported
- PDF (.pdf)
- Text (.txt)
- Word documents (.docx)
- HTML (.html)
- Markdown (.md)

### Data Processing
```bash
# Process all raw data
python -m backend.scripts.process_data --input data/raw --output data/processed

# Generate embeddings
python -m backend.scripts.embeddings --data data/processed
```

## 🚫 Important Notes
- **Never commit** processed data to version control
- **Keep raw data** small and focused
- **Use descriptive filenames** for easy identification
- **Document data sources** in a README within each subdirectory

## 📊 Data Quality
- Ensure data is clean and relevant
- Remove duplicates before processing
- Verify file integrity
- Check for encoding issues

---

*For more information, see the [data processing documentation](../docs/operations/data-processing.md)*
