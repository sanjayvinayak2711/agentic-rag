"""
Orchestrator Agent - Coordinates the workflow between other agents
"""

import time
import uuid
from typing import List, Dict, Any
import asyncio
from datetime import datetime
from utils.logger import setup_logger
from models.schemas import AgentResponse, QueryRequest, QueryResponse, DocumentInfo

logger = setup_logger(__name__)


class OrchestratorAgent:
    """Orchestrates the interaction between specialized agents"""
    
    def __init__(self, query_agent, retrieval_agent, generation_agent, validation_agent):
        self.query_agent = query_agent
        self.retrieval_agent = retrieval_agent
        self.generation_agent = generation_agent
        self.validation_agent = validation_agent
        self.max_iterations = 3
        
    async def process_query(self, request: QueryRequest) -> QueryResponse:
        """Process a query through the agent pipeline"""
        start_time = time.time()
        agent_steps = []
        
        try:
            # Step 1: Query Analysis
            logger.info(f"Analyzing query: {request.query}")
            query_analysis = await self.query_agent.analyze_query(request.query)
            agent_steps.append({
                "agent": "query_agent",
                "action": "analyze_query",
                "result": query_analysis,
                "timestamp": time.time()
            })
            
            # Step 2: Document Retrieval
            logger.info("Retrieving relevant documents")
            retrieved_docs = await self.retrieval_agent.retrieve(
                query_analysis["processed_query"],
                top_k=max(3, request.top_k)  # Force at least 3 results
            )
            logger.info(f"Retrieved {len(retrieved_docs)} documents")
            print("Retrieved docs:", retrieved_docs)  # Debug logging
            
            # Debug: Log retrieved document content
            if retrieved_docs:
                logger.info(f"Sample retrieved content: {retrieved_docs[0]['content'][:200]}...")
            else:
                logger.warning("No documents retrieved! Using fallback response.")
                # Safe fallback - no architecture change
                return {
                    "query": request.query,
                    "answer": "I couldn't find relevant info in the uploaded document. Try asking more specific questions or check if the file contains the answer.",
                    "sources": [],
                    "agent_steps": agent_steps,
                    "processing_time": time.time() - start_time,
                    "confidence_score": 0.1,
                    "conversation_id": str(uuid.uuid4())
                }
            
            agent_steps.append({
                "agent": "retrieval_agent",
                "action": "retrieve",
                "result": {"document_count": len(retrieved_docs)},
                "timestamp": time.time()
            })
            
            # Step 3: Response Generation (with iterative refinement)
            answer = None
            confidence = 0.0
            
            for iteration in range(self.max_iterations):
                logger.info(f"Generation iteration {iteration + 1}")
                
                # Generate response
                generation_result = await self.generation_agent.generate(
                    query_analysis["processed_query"],
                    retrieved_docs,
                    previous_answer=answer
                )
                
                answer = generation_result["answer"]
                confidence = generation_result["confidence"]
                
                agent_steps.append({
                    "agent": "generation_agent",
                    "action": "generate",
                    "result": generation_result,
                    "iteration": iteration + 1,
                    "timestamp": time.time()
                })
                
                # Validate the response
                validation_result = await self.validation_agent.validate(
                    request.query,
                    answer,
                    retrieved_docs
                )
                
                agent_steps.append({
                    "agent": "validation_agent",
                    "action": "validate",
                    "result": validation_result,
                    "iteration": iteration + 1,
                    "timestamp": time.time()
                })
                
                # If validation passes, break the loop
                if validation_result["is_valid"]:
                    logger.info("Response validation passed")
                    break
                else:
                    logger.info(f"Validation failed: {validation_result['reason']}")
                    # Use validation feedback for next iteration
                    query_analysis["feedback"] = validation_result["feedback"]
            
            processing_time = time.time() - start_time
            
            # Format sources properly for DocumentInfo schema
            sources = []
            for doc in retrieved_docs:
                # Create DocumentInfo object with required fields
                source_doc = DocumentInfo(
                    id=doc.get("chunk_id", str(uuid.uuid4())),
                    filename=doc["metadata"].get("filename", "Unknown"),
                    file_type=doc["metadata"].get("file_type", "unknown"),
                    size=doc["metadata"].get("size", 0),
                    upload_date=doc["metadata"].get("upload_date", datetime.now()),
                    chunk_count=doc["metadata"].get("chunk_count", 1),
                    metadata=doc["metadata"]
                )
                sources.append(source_doc)
            
            return QueryResponse(
                query=request.query,
                answer=answer,
                sources=sources,
                agent_steps=agent_steps,
                processing_time=processing_time,
                confidence_score=confidence,
                conversation_id=request.conversation_id or "default"
            )
            
        except Exception as e:
            logger.error(f"Error in orchestrator: {str(e)}")
            raise
    
    def get_agent_status(self) -> Dict[str, str]:
        """Get status of all agents"""
        return {
            "query_agent": "active",
            "retrieval_agent": "active", 
            "generation_agent": "active",
            "validation_agent": "active",
            "orchestrator": "active"
        }
