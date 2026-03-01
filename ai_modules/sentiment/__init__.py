"""
Sentiment Analysis Module
Analyzes customer message sentiment

Usage:
    from ai_modules.sentiment import SentimentAnalyzer, SentimentResult, SentimentLabel
    
    analyzer = SentimentAnalyzer()
    result = analyzer.analyze_text("Sản phẩm rất tốt!")
    print(result.label)  # POSITIVE
"""
from ai_modules.sentiment.analyzer import (
    SentimentAnalyzer,
    SentimentResult,
    SentimentLabel,
)

__all__ = ["SentimentAnalyzer", "SentimentResult", "SentimentLabel"]
