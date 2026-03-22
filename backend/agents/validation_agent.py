"""
Validation Agent - Validates the quality and accuracy of generated responses
"""

from typing import Dict, Any, List
import re
from backend.utils.logger import setup_logger

logger = setup_logger(__name__)


class ValidationAgent:
    """Agent responsible for validating generated responses"""
    
    def __init__(self):
        self.validation_rules = {
            "min_length": 20,
            "max_length": 2000,
            "required_elements": ["answer"],
            "forbidden_patterns": [
                r"i don't know",
                r"i cannot answer",
                r"as an ai",
                r"i'm sorry"
            ]
        }
    
    async def validate(self, query: str, answer: str, 
                      retrieved_docs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate a generated answer"""
        try:
            logger.info("Validating generated answer")
            
            validation_result = {
                "is_valid": True,
                "confidence": 0.0,
                "issues": [],
                "feedback": "",
                "scores": {}
            }
            
            # Perform various validation checks
            checks = [
                self._check_length(answer),
                self._check_content_quality(answer),
                self._check_relevance(query, answer),
                self._check_source_usage(answer, retrieved_docs),
                self._check_factual_consistency(answer, retrieved_docs),
                self._check_forbidden_patterns(answer)
            ]
            
            # Aggregate validation results
            total_score = 0
            max_score = 0
            
            for check_name, check_result in checks:
                validation_result["scores"][check_name] = check_result["score"]
                validation_result["issues"].extend(check_result.get("issues", []))
                total_score += check_result["score"]
                max_score += check_result["max_score"]
            
            # Calculate overall confidence
            if max_score > 0:
                validation_result["confidence"] = total_score / max_score
            
            # Determine if answer is valid
            validation_result["is_valid"] = (
                validation_result["confidence"] >= 0.6 and
                len([issue for issue in validation_result["issues"] if issue["severity"] == "high"]) == 0
            )
            
            # Generate feedback if not valid
            if not validation_result["is_valid"]:
                validation_result["feedback"] = self._generate_feedback(validation_result)
                validation_result["reason"] = validation_result["feedback"]  # Add reason field for compatibility
            
            logger.info(f"Validation completed. Valid: {validation_result['is_valid']}, Confidence: {validation_result['confidence']}")
            return validation_result
            
        except Exception as e:
            logger.error(f"Error in validation: {str(e)}")
            return {
                "is_valid": False,
                "confidence": 0.0,
                "issues": [{"type": "error", "message": str(e), "severity": "high"}],
                "feedback": "Validation failed due to an error.",
                "reason": "Validation failed due to an error.",  # Add reason field for compatibility
                "scores": {}
            }
    
    def _check_length(self, answer: str) -> Dict[str, Any]:
        """Check if answer length is appropriate"""
        issues = []
        score = 1.0
        
        if len(answer) < self.validation_rules["min_length"]:
            issues.append({
                "type": "length",
                "message": f"Answer is too short (minimum {self.validation_rules['min_length']} characters)",
                "severity": "medium"
            })
            score -= 0.3
        
        if len(answer) > self.validation_rules["max_length"]:
            issues.append({
                "type": "length", 
                "message": f"Answer is too long (maximum {self.validation_rules['max_length']} characters)",
                "severity": "low"
            })
            score -= 0.1
        
        return {"score": max(0.0, score), "max_score": 1.0, "issues": issues}
    
    def _check_content_quality(self, answer: str) -> Dict[str, Any]:
        """Check content quality metrics"""
        issues = []
        score = 1.0
        
        # Check for proper sentence structure
        sentences = re.split(r'[.!?]+', answer)
        if len(sentences) < 2:
            issues.append({
                "type": "structure",
                "message": "Answer lacks proper sentence structure",
                "severity": "medium"
            })
            score -= 0.2
        
        # Check for repetitive content
        words = answer.lower().split()
        if len(set(words)) / len(words) < 0.5:
            issues.append({
                "type": "repetition",
                "message": "Answer contains too much repetition",
                "severity": "medium"
            })
            score -= 0.2
        
        # Check for vague statements
        vague_phrases = ["might be", "could be", "perhaps", "maybe"]
        for phrase in vague_phrases:
            if phrase in answer.lower():
                issues.append({
                    "type": "vagueness",
                    "message": f"Answer contains vague phrase: '{phrase}'",
                    "severity": "low"
                })
                score -= 0.1
        
        return {"score": max(0.0, score), "max_score": 1.0, "issues": issues}
    
    def _check_relevance(self, query: str, answer: str) -> Dict[str, Any]:
        """Check if answer is relevant to the query"""
        issues = []
        score = 1.0
        
        query_words = set(query.lower().split())
        answer_words = set(answer.lower().split())
        
        # Calculate word overlap
        overlap = len(query_words.intersection(answer_words))
        overlap_ratio = overlap / len(query_words) if query_words else 0
        
        if overlap_ratio < 0.2:
            issues.append({
                "type": "relevance",
                "message": "Answer doesn't seem to address the query directly",
                "severity": "high"
            })
            score -= 0.4
        elif overlap_ratio < 0.5:
            issues.append({
                "type": "relevance",
                "message": "Answer has limited relevance to the query",
                "severity": "medium"
            })
            score -= 0.2
        
        return {"score": max(0.0, score), "max_score": 1.0, "issues": issues}
    
    def _check_source_usage(self, answer: str, retrieved_docs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Check if answer properly uses retrieved sources"""
        issues = []
        score = 1.0
        
        if not retrieved_docs:
            issues.append({
                "type": "sources",
                "message": "No sources were provided for validation",
                "severity": "medium"
            })
            score -= 0.3
            return {"score": max(0.0, score), "max_score": 1.0, "issues": issues}
        
        # Check if answer mentions sources
        has_citations = any(word in answer.lower() for word in ["according to", "source", "document", "based on"])
        
        if not has_citations and len(retrieved_docs) > 0:
            issues.append({
                "type": "citation",
                "message": "Answer doesn't cite its sources",
                "severity": "low"
            })
            score -= 0.1
        
        return {"score": max(0.0, score), "max_score": 1.0, "issues": issues}
    
    def _check_factual_consistency(self, answer: str, retrieved_docs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Check factual consistency with sources"""
        issues = []
        score = 1.0
        
        if not retrieved_docs:
            return {"score": 0.5, "max_score": 1.0, "issues": []}
        
        # Simple consistency check - can be enhanced with more sophisticated methods
        answer_lower = answer.lower()
        for doc in retrieved_docs:
            content_lower = doc["content"].lower()
            
            # Check if answer contains information not in sources
            answer_words = set(answer_lower.split())
            content_words = set(content_lower.split())
            
            # If answer has many words not in any source, flag it
            unique_words = answer_words - content_words
            if len(unique_words) > len(answer_words) * 0.3:
                issues.append({
                    "type": "consistency",
                    "message": "Answer may contain information not found in sources",
                    "severity": "medium"
                })
                score -= 0.2
                break
        
        return {"score": max(0.0, score), "max_score": 1.0, "issues": issues}
    
    def _check_forbidden_patterns(self, answer: str) -> Dict[str, Any]:
        """Check for forbidden patterns in answer"""
        issues = []
        score = 1.0
        
        answer_lower = answer.lower()
        
        for pattern in self.validation_rules["forbidden_patterns"]:
            if re.search(pattern, answer_lower):
                issues.append({
                    "type": "forbidden",
                    "message": f"Answer contains forbidden pattern: {pattern}",
                    "severity": "high"
                })
                score -= 0.5
        
        return {"score": max(0.0, score), "max_score": 1.0, "issues": issues}
    
    def _generate_feedback(self, validation_result: Dict[str, Any]) -> str:
        """Generate feedback for improving the answer"""
        high_issues = [issue for issue in validation_result["issues"] if issue["severity"] == "high"]
        medium_issues = [issue for issue in validation_result["issues"] if issue["severity"] == "medium"]
        
        feedback_parts = []
        
        if high_issues:
            feedback_parts.append("Please address these critical issues:")
            for issue in high_issues:
                feedback_parts.append(f"- {issue['message']}")
        
        if medium_issues:
            feedback_parts.append("Consider these improvements:")
            for issue in medium_issues:
                feedback_parts.append(f"- {issue['message']}")
        
        if not feedback_parts:
            feedback_parts.append("The answer needs general improvement in quality and relevance.")
        
        return "\n".join(feedback_parts)
