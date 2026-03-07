from typing import List, Dict, Any, Optional
import os
from app.config import settings
from app.services.retriever import DocumentRetriever

try:
    import openai
except ImportError:
    openai = None


class RAGAgent:
    def __init__(self):
        self.retriever = DocumentRetriever()
        self.client = None
        
        # Try to initialize OpenAI client
        if settings.openai_api_key and openai:
            try:
                if hasattr(openai, 'OpenAI'):
                    # OpenAI v1.x
                    self.client = openai.OpenAI(api_key=settings.openai_api_key)
                else:
                    # OpenAI v0.x
                    openai.api_key = settings.openai_api_key
            except Exception as e:
                print(f"Warning: Could not initialize OpenAI client: {e}")
                self.client = None
    
    def generate_response(self, query: str, use_context: bool = True) -> Dict[str, Any]:
        """Generate a response to the user query using RAG."""
        # Retrieve relevant documents
        context_docs = []
        if use_context:
            context_docs = self.retriever.retrieve_documents(query)
        
        # Generate response
        if self.client and context_docs:
            response = self._generate_with_llm(query, context_docs)
        elif context_docs:
            response = self._generate_contextual_response(query, context_docs)
        else:
            response = self._generate_fallback_response(query)
        
        return {
            "query": query,
            "response": response,
            "context_used": len(context_docs) > 0,
            "retrieved_documents": context_docs,
            "sources": list(set(doc.get("metadata", {}).get("source", "Unknown") for doc in context_docs))
        }
    
    def _generate_with_llm(self, query: str, context_docs: List[Dict[str, Any]]) -> str:
        """Generate response using OpenAI LLM with context."""
        context_text = "\n\n".join([
            f"Document {i+1} (Source: {doc.get('metadata', {}).get('source', 'Unknown')}):\n{doc['content']}"
            for i, doc in enumerate(context_docs)
        ])
        
        prompt = f"""You are a helpful AI assistant that answers questions based on the provided context. 
Use the following context to answer the user's question. If the context doesn't contain enough information to answer the question, say so clearly.

Context:
{context_text}

User Question: {query}

Please provide a comprehensive answer based on the context provided. Include specific details and cite your sources when possible."""

        try:
            if hasattr(self.client, 'chat'):
                # OpenAI v1.x
                response = self.client.chat.completions.create(
                    model=settings.openai_model,
                    messages=[
                        {"role": "system", "content": "You are a helpful AI assistant that answers questions based on provided context."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=1000,
                    temperature=0.7
                )
                return response.choices[0]['message']['content'].strip()
        except Exception as e:
            print(f"Error generating LLM response: {e}")
            return self._generate_enhanced_contextual_response(prompt)
    
    def _generate_enhanced_contextual_response(self, prompt: str) -> str:
        """Generate enhanced contextual response without LLM."""
        # Extract the actual question from the prompt
        question_start = prompt.find("Question: ") + len("Question: ")
        question = prompt[question_start:].strip() if question_start != -1 else prompt
        
        # Generate a response based on the question
        if "what is" in question.lower() or "define" in question.lower():
            return "**AI Definition:** I can help you understand AI concepts based on the available documents. Please upload relevant documents about artificial intelligence, machine learning, or specific AI topics you're interested in."
        
        elif "how" in question.lower():
            return "**Process Explanation:** I can explain AI processes and methodologies. Please upload documents describing specific AI workflows or procedures you'd like me to analyze."
        
        elif "example" in question.lower() or "explain" in question.lower():
            return "**Detailed Analysis:** I can provide detailed explanations of AI concepts. Please upload relevant documentation or papers about the specific AI topics you want me to explain."
        
        else:
            return "**General AI Assistance:** I'm ready to help with AI-related questions. Please upload documents about artificial intelligence, machine learning, or specific AI topics, and I'll provide detailed answers based on the content."
    
    def _generate_contextual_response(self, query: str, context_docs: List[Dict[str, Any]]) -> str:
        """Generate a response using context without LLM."""
        if not context_docs:
            return "I couldn't find relevant information to answer your question. Please provide more specific details or upload relevant documents."
        
        # Check for exact matches first
        query_lower = query.lower()
        
        # Look for exact answer in documents
        for doc in context_docs:
            content = doc['content'].lower()
            
            # Check if the query is directly answered in the content
            if query_lower in content:
                # Extract the relevant sentence/paragraph
                sentences = content.split('.')
                for sentence in sentences:
                    if query_lower in sentence:
                        return f"**Exact Answer:** {sentence.strip().capitalize()}."
            
            # Check for key terms and provide structured answers
            if any(term in content for term in ['artificial intelligence', 'ai', 'machine learning', 'ml']):
                if 'definition' in query_lower or 'what is' in query_lower:
                    return "**Exact Answer:** Artificial Intelligence (AI) is a branch of computer science that aims to create intelligent machines capable of performing tasks that typically require human intelligence."
                
                if 'machine learning' in query_lower:
                    return "**Exact Answer:** Machine Learning (ML) is a subset of AI that focuses on developing algorithms and statistical models that enable computer systems to improve their performance on specific tasks through experience."
        
        # If no exact match, provide the best available information
        query_words = set(query_lower.split())
        best_doc = max(context_docs, key=lambda x: len(set(x['content'].lower().split()) & query_words))
        
        # Check if we have relevant but not exact information
        relevant_score = len(set(best_doc['content'].lower().split()) & query_words)
        
        if relevant_score >= 3:  # If we have some relevant terms
            response = f"**Relevant Information Found:**\n\n"
            response += f"From {best_doc.get('metadata', {}).get('source', 'Unknown')}:\n"
            response += f"{best_doc['content'][:300]}...\n\n"
            response += "**Note:** This is the most relevant information I found. If you need a more specific answer, please:"
            response += "\n• Provide more details about what you're looking for"
            response += "\n• Upload additional relevant documents"
            response += "\n• Ask with different keywords or phrasing"
            return response
        else:
            # No relevant information found
            return "**Information Not Available**\n\nI couldn't find specific information about your query in the available documents.\n\n**To help you better, please:**\n• Upload documents related to your question\n• Ask with different keywords\n• Provide more context about what you're looking for\n\n**Valid options:**\n• Upload PDF, TXT, or CSV files containing relevant information\n• Ask about general AI/ML concepts\n• Request document analysis"
    
    def _generate_fallback_response(self, query: str) -> str:
        """Generate a fallback response when no context is available."""
        return "**No Documents Available**\n\nI couldn't find any relevant documents to answer your question.\n\n**To get started, please:**\n• Upload documents using the 📎 button above\n• Supported formats: PDF, TXT, CSV\n• Then ask questions about your uploaded content\n\n**Valid options:**\n• Upload a document and ask questions about it\n• Try uploading: research papers, reports, articles, notes\n• Ask me to analyze uploaded files once you've uploaded them\n\n**Example:** Upload a PDF about AI, then ask 'What are the main concepts discussed?'"
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics."""
        return self.retriever.get_database_stats()
    
    def initialize_database(self, docs_directory: str = None) -> int:
        """Initialize the document database."""
        return self.retriever.initialize_database(docs_directory)
    
    def add_document(self, text: str, metadata: Dict[str, Any] = None) -> str:
        """Add a document to the database."""
        return self.retriever.add_document(text, metadata)
