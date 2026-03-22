"""
Tests for Agentic-RAG agents
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from backend.agents.orchestrator import OrchestratorAgent
from backend.agents.query_agent import QueryAgent
from backend.agents.retrieval_agent import RetrievalAgent
from backend.agents.generation_agent import GenerationAgent
from backend.agents.validation_agent import ValidationAgent
from backend.models.schemas import QueryRequest


class TestQueryAgent:
    """Test cases for QueryAgent"""
    
    @pytest.fixture
    def query_agent(self):
        return QueryAgent()
    
    @pytest.mark.asyncio
    async def test_analyze_query_simple(self, query_agent):
        """Test simple query analysis"""
        query = "What is machine learning?"
        result = await query_agent.analyze_query(query)
        
        assert result["original_query"] == query
        assert "processed_query" in result
        assert "query_type" in result
        assert "keywords" in result
        assert "intent" in result
        assert "search_terms" in result
        assert result["query_type"] == "question"
        assert "machine" in result["keywords"]
        assert "learning" in result["keywords"]
    
    @pytest.mark.asyncio
    async def test_analyze_query_comparison(self, query_agent):
        """Test comparison query analysis"""
        query = "Compare Python and JavaScript"
        result = await query_agent.analyze_query(query)
        
        assert result["query_type"] == "comparison"
        assert result["intent"] == "compare_items"
    
    @pytest.mark.asyncio
    async def test_analyze_query_empty(self, query_agent):
        """Test empty query analysis"""
        query = ""
        result = await query_agent.analyze_query(query)
        
        assert result["processed_query"] == ""
        assert result["query_type"] == "general"
    
    @pytest.mark.asyncio
    async def test_extract_keywords(self, query_agent):
        """Test keyword extraction"""
        query = "The quick brown fox jumps over the lazy dog"
        keywords = query_agent._extract_keywords(query)
        
        assert "quick" in keywords
        assert "brown" in keywords
        assert "fox" in keywords
        assert "the" not in keywords  # Stop word should be removed


class TestRetrievalAgent:
    """Test cases for RetrievalAgent"""
    
    @pytest.fixture
    def retrieval_agent(self):
        with patch('backend.agents.retrieval_agent.VectorStore'), \
             patch('backend.agents.retrieval_agent.EmbeddingGenerator'):
            return RetrievalAgent()
    
    @pytest.mark.asyncio
    async def test_retrieve_with_results(self, retrieval_agent):
        """Test successful document retrieval"""
        # Mock vector store response
        mock_results = [
            {
                "content": "Machine learning is a subset of AI",
                "metadata": {"filename": "doc1.txt"},
                "score": 0.9,
                "id": "doc1"
            }
        ]
        
        retrieval_agent.vector_store.similarity_search = AsyncMock(return_value=mock_results)
        
        results = await retrieval_agent.retrieve("What is machine learning?", top_k=5)
        
        assert len(results) == 1
        assert results[0]["content"] == "Machine learning is a subset of AI"
        assert results[0]["score"] == 0.9
    
    @pytest.mark.asyncio
    async def test_retrieve_no_results(self, retrieval_agent):
        """Test retrieval with no results"""
        retrieval_agent.vector_store.similarity_search = AsyncMock(return_value=[])
        
        results = await retrieval_agent.retrieve("Random query", top_k=5)
        
        assert len(results) == 0
    
    @pytest.mark.asyncio
    async def test_hybrid_search(self, retrieval_agent):
        """Test hybrid search functionality"""
        mock_semantic = [{"content": "semantic result", "score": 0.8, "id": "sem1"}]
        mock_metadata = [{"content": "metadata result", "score": 0.7, "id": "meta1"}]
        
        retrieval_agent.retrieve = AsyncMock(side_effect=[mock_semantic, mock_metadata])
        
        results = await retrieval_agent.hybrid_search("test query")
        
        assert len(results) == 2
        assert results[0]["score"] >= results[1]["score"]  # Should be sorted by score


class TestGenerationAgent:
    """Test cases for GenerationAgent"""
    
    @pytest.fixture
    def generation_agent(self):
        with patch('backend.agents.generation_agent.LLMClient'):
            return GenerationAgent()
    
    @pytest.mark.asyncio
    async def test_generate_response(self, generation_agent):
        """Test response generation"""
        # Mock LLM response
        mock_response = "Machine learning is a method of data analysis..."
        generation_agent.llm_client.generate_response = AsyncMock(return_value=mock_response)
        
        retrieved_docs = [{"content": "Machine learning definition...", "score": 0.9}]
        
        result = await generation_agent.generate("What is machine learning?", retrieved_docs)
        
        assert result["answer"] == mock_response
        assert "confidence" in result
        assert "processing_time" in result
        assert result["context_used"] == 1
    
    @pytest.mark.asyncio
    async def test_refine_answer(self, generation_agent):
        """Test answer refinement"""
        original_answer = "Basic answer"
        feedback = "Add more detail"
        context = ["Detailed context"]
        
        mock_refined = "Detailed refined answer"
        generation_agent.llm_client.generate_response = AsyncMock(return_value=mock_refined)
        
        result = await generation_agent.refine_answer(original_answer, feedback, context)
        
        assert result["answer"] == mock_refined
        assert result["refined"] is True
    
    def test_calculate_confidence(self, generation_agent):
        """Test confidence calculation"""
        response = "This is a detailed response with proper structure."
        context = ["Relevant context"]
        
        confidence = generation_agent._calculate_confidence(response, context, "test query")
        
        assert 0 <= confidence <= 1
        assert confidence > 0.5  # Should be reasonably confident for good response


class TestValidationAgent:
    """Test cases for ValidationAgent"""
    
    @pytest.fixture
    def validation_agent(self):
        return ValidationAgent()
    
    @pytest.mark.asyncio
    async def test_validate_good_answer(self, validation_agent):
        """Test validation of a good answer"""
        query = "What is machine learning?"
        answer = "Machine learning is a subset of artificial intelligence that enables systems to learn and improve from experience."
        retrieved_docs = [{"content": "Machine learning is a subset of AI...", "score": 0.9}]
        
        result = await validation_agent.validate(query, answer, retrieved_docs)
        
        assert result["is_valid"] is True
        assert result["confidence"] > 0.6
        assert len(result["issues"]) == 0
    
    @pytest.mark.asyncio
    async def test_validate_short_answer(self, validation_agent):
        """Test validation of a short answer"""
        query = "What is machine learning?"
        answer = "AI."
        retrieved_docs = [{"content": "Machine learning is a subset of AI...", "score": 0.9}]
        
        result = await validation_agent.validate(query, answer, retrieved_docs)
        
        assert result["is_valid"] is False
        assert result["confidence"] < 0.6
        assert any(issue["type"] == "length" for issue in result["issues"])
    
    @pytest.mark.asyncio
    async def test_validate_irrelevant_answer(self, validation_agent):
        """Test validation of irrelevant answer"""
        query = "What is machine learning?"
        answer = "The weather is nice today."
        retrieved_docs = [{"content": "Machine learning is a subset of AI...", "score": 0.9}]
        
        result = await validation_agent.validate(query, answer, retrieved_docs)
        
        assert result["is_valid"] is False
        assert any(issue["type"] == "relevance" for issue in result["issues"])
    
    @pytest.mark.asyncio
    async def test_validate_forbidden_pattern(self, validation_agent):
        """Test validation with forbidden patterns"""
        query = "What is machine learning?"
        answer = "I don't know the answer to your question."
        retrieved_docs = [{"content": "Machine learning is a subset of AI...", "score": 0.9}]
        
        result = await validation_agent.validate(query, answer, retrieved_docs)
        
        assert result["is_valid"] is False
        assert any(issue["type"] == "forbidden" for issue in result["issues"])
    
    def test_generate_feedback(self, validation_agent):
        """Test feedback generation"""
        validation_result = {
            "is_valid": False,
            "issues": [
                {"type": "length", "message": "Answer too short", "severity": "medium"},
                {"type": "relevance", "message": "Not relevant", "severity": "high"}
            ]
        }
        
        feedback = validation_agent._generate_feedback(validation_result)
        
        assert "critical issues" in feedback
        assert "Answer too short" in feedback
        assert "Not relevant" in feedback


class TestOrchestratorAgent:
    """Test cases for OrchestratorAgent"""
    
    @pytest.fixture
    def orchestrator(self):
        # Mock all agents
        with patch('backend.agents.orchestrator.QueryAgent') as mock_query, \
             patch('backend.agents.orchestrator.RetrievalAgent') as mock_retrieval, \
             patch('backend.agents.orchestrator.GenerationAgent') as mock_generation, \
             patch('backend.agents.orchestrator.ValidationAgent') as mock_validation:
            
            query_agent = Mock()
            query_agent.analyze_query = AsyncMock(return_value={
                "processed_query": "machine learning",
                "query_type": "question",
                "keywords": ["machine", "learning"],
                "intent": "seek_information",
                "search_terms": ["machine learning"]
            })
            
            retrieval_agent = Mock()
            retrieval_agent.retrieve = AsyncMock(return_value=[
                {"content": "Machine learning definition...", "metadata": {"filename": "doc1.txt"}, "score": 0.9}
            ])
            
            generation_agent = Mock()
            generation_agent.generate = AsyncMock(return_value={
                "answer": "Machine learning is a subset of AI...",
                "confidence": 0.8,
                "processing_time": 1.5
            })
            
            validation_agent = Mock()
            validation_agent.validate = AsyncMock(return_value={
                "is_valid": True,
                "confidence": 0.8,
                "issues": [],
                "feedback": ""
            })
            
            return OrchestratorAgent(query_agent, retrieval_agent, generation_agent, validation_agent)
    
    @pytest.mark.asyncio
    async def test_process_query_success(self, orchestrator):
        """Test successful query processing"""
        request = QueryRequest(query="What is machine learning?", top_k=5, use_agents=True)
        
        response = await orchestrator.process_query(request)
        
        assert response.query == "What is machine learning?"
        assert response.answer == "Machine learning is a subset of AI..."
        assert len(response.sources) == 1
        assert response.confidence_score == 0.8
        assert response.processing_time > 0
        assert len(response.agent_steps) > 0
    
    @pytest.mark.asyncio
    async def test_process_query_with_validation_failure(self, orchestrator):
        """Test query processing with validation failure"""
        # Mock validation to fail first time, pass second time
        orchestrator.validation_agent.validate.side_effect = [
            {"is_valid": False, "confidence": 0.3, "issues": [{"type": "quality", "message": "Low quality"}], "feedback": "Improve quality"},
            {"is_valid": True, "confidence": 0.8, "issues": [], "feedback": ""}
        ]
        
        request = QueryRequest(query="What is machine learning?", top_k=5, use_agents=True)
        
        response = await orchestrator.process_query(request)
        
        assert response.answer == "Machine learning is a subset of AI..."
        # Should have called generation twice (initial + refinement)
        assert orchestrator.generation_agent.generate.call_count == 2
    
    def test_get_agent_status(self, orchestrator):
        """Test agent status retrieval"""
        status = orchestrator.get_agent_status()
        
        assert all(status == "active" for status in status.values())
        assert "query_agent" in status
        assert "retrieval_agent" in status
        assert "generation_agent" in status
        assert "validation_agent" in status
        assert "orchestrator" in status


# Integration tests
class TestAgentIntegration:
    """Integration tests for agent system"""
    
    @pytest.mark.asyncio
    async def test_full_pipeline(self):
        """Test the complete agent pipeline with mocked dependencies"""
        # This would be a more comprehensive integration test
        # For now, we'll test the basic flow
        
        with patch('backend.agents.orchestrator.QueryAgent'), \
             patch('backend.agents.orchestrator.RetrievalAgent'), \
             patch('backend.agents.orchestrator.GenerationAgent'), \
             patch('backend.agents.orchestrator.ValidationAgent'):
            
            orchestrator = OrchestratorAgent(
                QueryAgent(), RetrievalAgent(), GenerationAgent(), ValidationAgent()
            )
            
            # Test that the orchestrator can be instantiated
            assert orchestrator is not None
            assert orchestrator.max_iterations == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
