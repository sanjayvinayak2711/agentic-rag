# Uploads Directory

This directory handles user-uploaded files and temporary processing data.

## 📁 Directory Structure

- **temp/** - Temporary upload files
  - Files during processing
  - Automatically cleaned up
  - Session-based storage

- **processed/** - Processed user uploads
  - Successfully processed documents
  - Extracted text and metadata
  - Ready for RAG indexing

## 🔄 File Lifecycle

1. **Upload** → `uploads/temp/`
2. **Processing** → Extract text, validate format
3. **Completion** → Move to `uploads/processed/`
4. **Cleanup** → Remove from temp after processing

## 📋 Supported File Types

### Document Formats
- **PDF** (.pdf) - Primary format
- **Text** (.txt) - Plain text files
- **Word** (.docx) - Microsoft Word
- **HTML** (.html) - Web pages

### File Size Limits
- **Maximum**: 50MB per file
- **Recommended**: <10MB for optimal performance
- **Batch**: Up to 10 files simultaneously

## 🛡️ Security Considerations

### File Validation
- File type verification
- Size limit enforcement
- Malware scanning (if enabled)
- Content sanitization

### Access Control
- Session-based isolation
- Automatic cleanup
- No direct file access
- Secure temporary storage

## 🧹 Cleanup Policies

### Automatic Cleanup
```bash
# Clean temp files older than 1 hour
python -m backend.scripts.cleanup --temp --age 1h

# Clean processed files older than 30 days
python -m backend.scripts.cleanup --processed --age 30d
```

### Manual Cleanup
```bash
# Clean all temp files
make clean-temp

# Clean old processed files
make clean-processed
```

## 📊 Storage Management

### Monitoring
```bash
# Check storage usage
python -m backend.scripts.storage-stats

# List recent uploads
python -m backend.scripts.recent-uploads
```

### Optimization
- Compress processed text
- Remove redundant files
- Archive old uploads
- Monitor disk usage

## 🔧 Configuration

Environment variables in `.env`:
```bash
# Upload settings
MAX_FILE_SIZE=52428800  # 50MB in bytes
UPLOAD_DIR=uploads
TEMP_DIR=uploads/temp
PROCESSED_DIR=uploads/processed

# Cleanup settings
CLEANUP_INTERVAL=3600  # 1 hour in seconds
TEMP_FILE_LIFETIME=3600  # 1 hour
PROCESSED_FILE_LIFETIME=2592000  # 30 days
```

## 🚨 Troubleshooting

### Common Issues

#### Upload Fails
- Check file size limits
- Verify file format support
- Ensure disk space available
- Check permissions

#### Processing Stuck
- Monitor temp directory size
- Check system resources
- Review error logs
- Restart processing queue

#### Storage Full
- Run cleanup scripts
- Archive old files
- Increase disk space
- Adjust retention policies

### Debug Commands
```bash
# Check upload directory status
python -m backend.scripts.debug-uploads

# Test file processing
python -m backend.scripts.test-processing --file test.pdf

# Monitor active uploads
python -m backend.scripts.monitor-uploads
```

## 📚 Related Documentation

- [API Endpoints](../docs/api/upload.md)
- [File Processing](../docs/operations/file-processing.md)
- [Security Guide](../docs/architecture/security.md)

---

*For issues with file uploads, check the [troubleshooting guide](../docs/operations/troubleshooting.md)*
