# Agentic RAG - Document Q&A System

A powerful Retrieval-Augmented Generation (RAG) system that allows you to upload documents and ask questions about them using AI. Built with FastAPI, ChromaDB, and modern web technologies.

## Features

- 🤖 **Intelligent Q&A**: Ask questions about your documents and get accurate answers
- 📄 **Multiple File Formats**: Support for PDF, TXT, and CSV files
- 🔍 **Semantic Search**: Advanced vector-based document retrieval
- 🎨 **Modern UI**: Clean, responsive web interface
- 🚀 **FastAPI Backend**: High-performance async API
- 💾 **Vector Database**: Efficient document storage with ChromaDB
- 🧠 **OpenAI Integration**: Optional LLM-powered responses
- 🐳 **Docker Support**: Easy deployment with Docker

## Quick Start

### Prerequisites

- Python 3.8+
- pip or poetry
- (Optional) OpenAI API key for enhanced responses

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd agentic-rag
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables** (optional)
   ```bash
   # Create .env file
   echo "OPENAI_API_KEY=your_openai_api_key_here" > .env
   ```

4. **Run the application**
   ```bash
   python -m app.main
   ```

5. **Access the application**
   - Open your browser and go to `http://localhost:8000`
   - API documentation available at `http://localhost:8000/docs`

### Docker Deployment

1. **Build and run with Docker Compose**
   ```bash
   docker-compose up --build
   ```

2. **Or build and run manually**
   ```bash
   docker build -t agentic-rag .
   docker run -p 8000:8000 -v $(pwd)/data:/app/data agentic-rag
   ```

## Usage

### 1. Add Documents

You can add documents in several ways:

- **Upload Files**: Use the web interface to upload PDF, TXT, or CSV files
- **Initialize Database**: Load all documents from the `data/docs` directory
- **Add Text**: Paste text directly into the interface

### 2. Ask Questions

Once documents are loaded, you can:

- Type your question in the query box
- Choose whether to use document context (recommended)
- Press Enter+Ctrl or click "Ask" to submit

### 3. View Results

The system will provide:

- **AI-generated response** based on your documents
- **Source information** showing which documents were used
- **Similarity scores** for retrieved documents
- **Context snippets** from relevant documents

## API Endpoints

### Query Documents
```http
POST /api/query
Content-Type: application/json

{
  "query": "What is machine learning?",
  "use_context": true
}
```

### Add Document
```http
POST /api/documents
Content-Type: application/json

{
  "text": "Machine learning is a subset of AI...",
  "metadata": {"source": "manual"}
}
```

### Upload File
```http
POST /api/upload
Content-Type: multipart/form-data

file: [your_file.pdf]
```

### Get Statistics
```http
GET /api/stats
```

### Initialize Database
```http
POST /api/initialize
```

## Configuration

The application can be configured using environment variables or a `.env` file:

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | `None` | OpenAI API key for enhanced responses |
| `EMBEDDING_MODEL` | `all-MiniLM-L6-v2` | Sentence transformer model |
| `CHROMA_PERSIST_DIRECTORY` | `./data/chroma` | Vector database storage |
| `CHUNK_SIZE` | `1000` | Document chunk size |
| `CHUNK_OVERLAP` | `200` | Overlap between chunks |
| `MAX_RETRIEVED_DOCS` | `5` | Max documents to retrieve |
| `DEBUG` | `true` | Enable debug mode |

## Architecture

```
agentic-rag/
├── app/
│   ├── main.py                 # FastAPI application
│   ├── config.py               # Configuration settings
│   ├── routes/
│   │   └── query.py            # API routes
│   ├── services/
│   │   ├── agent.py            # RAG agent logic
│   │   └── retriever.py        # Document retrieval
│   └── utils/
│       └── embeddings.py       # Text embedding utilities
├── ui/
│   ├── index.html              # Web interface
│   ├── main.js                 # Frontend JavaScript
│   └── styles.css              # Styling
├── data/
│   └── docs/                   # Document storage
├── tests/
│   └── test_app.py             # Unit tests
└── requirements.txt            # Python dependencies
```

## How It Works

1. **Document Processing**: Documents are chunked and converted to vector embeddings
2. **Vector Storage**: Embeddings are stored in ChromaDB for efficient similarity search
3. **Query Processing**: User queries are embedded and matched against document vectors
4. **Response Generation**: Retrieved context is used to generate accurate responses
5. **Source Attribution**: Responses include source information for transparency

## Testing

Run the test suite:

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest tests/

# Run with coverage
pytest tests/ --cov=app --cov-report=html
```

## Development

### Setting up the development environment

1. **Clone and install dependencies**
   ```bash
   git clone <repository-url>
   cd agentic-rag
   pip install -r requirements.txt
   pip install -e .  # Install in development mode
   ```

2. **Run in development mode**
   ```bash
   python -m app.main --reload
   ```

3. **Code formatting and linting**
   ```bash
   pip install black flake8 mypy
   black app/
   flake8 app/
   mypy app/
   ```

### Adding New Features

1. **New document types**: Extend the `EmbeddingManager.process_document()` method
2. **New embedding models**: Modify the configuration and embedding utilities
3. **Additional API endpoints**: Add new routes in `app/routes/`
4. **UI enhancements**: Update HTML, CSS, and JavaScript in the `ui/` directory

## Performance Considerations

- **Embedding Model**: The default `all-MiniLM-L6-v2` provides a good balance of speed and accuracy
- **Chunk Size**: Larger chunks provide more context but slower processing
- **Database Size**: ChromaDB scales well, but consider pagination for large document sets
- **Caching**: Responses can be cached for frequently asked questions

## Troubleshooting

### Common Issues

1. **Memory Issues**: Reduce `CHUNK_SIZE` if you encounter memory errors
2. **Slow Responses**: Consider using a smaller embedding model or fewer retrieved documents
3. **OpenAI API Errors**: Check your API key and rate limits
4. **Document Parsing Errors**: Ensure documents are in supported formats (PDF, TXT, CSV)

### Debug Mode

Enable debug mode for detailed logging:

```bash
export DEBUG=true
python -m app.main
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) - Modern, fast web framework for building APIs
- [ChromaDB](https://www.trychroma.com/) - Open-source embedding database
- [Sentence Transformers](https://www.sbert.net/) - State-of-the-art text embeddings
- [OpenAI](https://openai.com/) - AI language models for enhanced responses

## Support

For issues and questions:

1. Check the [troubleshooting section](#troubleshooting)
2. Search existing [GitHub issues](https://github.com/your-repo/agentic-rag/issues)
3. Create a new issue with detailed information

---

**Built with ❤️ for intelligent document Q&A**
