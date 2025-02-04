from abc import ABC, abstractmethod
from typing import TypeVar, Generic

T = TypeVar('T')

class IGptAnalyzer(ABC, Generic[T]):
    """Base interface for GPT analyzers"""
    
    @abstractmethod
    def analyze(self, call_text: str) -> T:
        """
        Analyze call text and return structured results
        
        Args:
            call_text: The transcribed call text to analyze
            
        Returns:
            Structured analysis results of type T
        """
        pass
