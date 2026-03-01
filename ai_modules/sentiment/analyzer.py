"""
Sentiment Analyzer - Phân tích cảm xúc tin nhắn khách hàng
Hỗ trợ: Gemini (primary) > OpenAI (fallback) > Rule-based (offline)

Features:
- analyze_text: Phân tích 1 tin nhắn
- analyze_ticket: Phân tích toàn bộ ticket
- analyze_conversation: Phân tích cuộc hội thoại
- batch_analyze: Phân tích hàng loạt
"""
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from enum import Enum
import os
import re
import json

from ai_modules.core.config import ai_config


class SentimentLabel(str, Enum):
    """Nhãn cảm xúc"""
    POSITIVE = "POSITIVE"
    NEUTRAL = "NEUTRAL"
    NEGATIVE = "NEGATIVE"


@dataclass
class SentimentResult:
    """Kết quả phân tích cảm xúc"""
    score: float           # -1.0 (rất tiêu cực) đến 1.0 (rất tích cực)
    label: SentimentLabel  # POSITIVE / NEUTRAL / NEGATIVE
    confidence: float      # 0.0 đến 1.0
    emotions: Dict[str, float] = field(default_factory=dict)  # joy, anger, sadness, etc.
    provider: str = "rule_based"  # gemini / openai / rule_based
    text_preview: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "score": round(self.score, 4),
            "label": self.label.value,
            "confidence": round(self.confidence, 4),
            "emotions": {k: round(v, 4) for k, v in self.emotions.items()},
            "provider": self.provider,
            "text_preview": self.text_preview[:100]
        }


class SentimentAnalyzer:
    """
    AI-powered Sentiment Analyzer

    LLM Priority: Gemini > OpenAI > Rule-based (offline)

    Usage:
        analyzer = SentimentAnalyzer()
        result = analyzer.analyze_text("Sản phẩm rất tốt, giao hàng nhanh!")
        print(result.label)  # POSITIVE
        print(result.score)  # 0.85
    """

    # ── Vietnamese keyword lexicons ──────────────────────────────
    _POSITIVE_KEYWORDS: List[str] = [
        "tốt", "tuyệt vời", "xuất sắc", "hài lòng", "thích", "yêu",
        "nhanh", "chất lượng", "đẹp", "tuyệt", "ổn", "ok", "good",
        "great", "excellent", "amazing", "happy", "love", "perfect",
        "chuyên nghiệp", "ấn tượng", "hấp dẫn", "tận tâm", "chu đáo",
        "cảm ơn", "thank", "thanks", "hợp lý", "phù hợp", "đáng tiền",
        "rẻ", "nhanh chóng", "đúng hẹn", "uy tín", "tin tưởng",
        "recommend", "gợi ý", "giới thiệu", "5 sao", "⭐"
    ]

    _NEGATIVE_KEYWORDS: List[str] = [
        "tệ", "kém", "chậm", "lỗi", "hỏng", "thất vọng", "tồi",
        "xấu", "dở", "không hài lòng", "bực", "tức", "giận",
        "bad", "terrible", "awful", "poor", "broken", "angry",
        "disappointed", "worst", "horrible", "frustrated",
        "gian lận", "lừa đảo", "scam", "chờ lâu", "không phản hồi",
        "khiếu nại", "hoàn tiền", "đổi trả", "trả hàng", "hủy",
        "chán", "phí tiền", "đắt", "không đáng", "vấn đề",
        "sai", "nhầm", "thiếu", "không được", "không hoạt động"
    ]

    _INTENSIFIERS: List[str] = [
        "rất", "cực kỳ", "vô cùng", "quá", "siêu", "khá",
        "hơi", "cũng", "really", "very", "extremely", "so"
    ]

    _NEGATORS: List[str] = [
        "không", "chẳng", "chả", "đâu", "no", "not", "never",
        "chưa", "không bao giờ", "ko", "k", "hem", "hông"
    ]

    def __init__(self):
        self.demo_mode = ai_config.demo_mode
        self._init_llm_client()

    def _init_llm_client(self):
        """
        Initialize LLM client
        Priority: Gemini > OpenAI > None (rule-based fallback)
        """
        self.llm_client = None
        self.llm_provider = None

        if self.demo_mode:
            print("[SentimentAnalyzer] Running in DEMO_MODE - using rule-based analysis")
            return

        # Try Gemini first
        gemini_key = os.getenv("GEMINI_API_KEY") or ai_config.gemini_api_key
        if gemini_key:
            try:
                from google import genai
                self.llm_client = genai.Client(api_key=gemini_key)
                self.llm_provider = "gemini"
                print("[SentimentAnalyzer] Using Gemini LLM")
                return
            except ImportError:
                print("[SentimentAnalyzer] google-genai not installed, trying OpenAI...")
            except Exception as e:
                print(f"[SentimentAnalyzer] Gemini init error: {e}")

        # Fallback to OpenAI
        openai_key = os.getenv("OPENAI_API_KEY") or ai_config.openai_api_key
        if openai_key:
            try:
                from openai import OpenAI
                self.llm_client = OpenAI(api_key=openai_key)
                self.llm_provider = "openai"
                print("[SentimentAnalyzer] Using OpenAI LLM")
                return
            except ImportError:
                print("[SentimentAnalyzer] openai not installed")
            except Exception as e:
                print(f"[SentimentAnalyzer] OpenAI init error: {e}")

        print("[SentimentAnalyzer] No LLM configured - using rule-based analysis")

    # ─── Public API ──────────────────────────────────────────────

    def analyze_text(self, text: str) -> SentimentResult:
        """
        Phân tích cảm xúc một đoạn text.

        Args:
            text: Nội dung cần phân tích

        Returns:
            SentimentResult
        """
        if not text or not text.strip():
            return SentimentResult(
                score=0.0,
                label=SentimentLabel.NEUTRAL,
                confidence=1.0,
                provider="none",
                text_preview=""
            )

        text = text.strip()

        # Use LLM if available, otherwise rule-based
        if self.llm_client and not self.demo_mode:
            return self._analyze_with_llm(text)
        return self._analyze_rule_based(text)

    def analyze_ticket(
        self,
        ticket_id: str,
        db=None
    ) -> Dict[str, Any]:
        """
        Phân tích cảm xúc toàn bộ ticket.

        Args:
            ticket_id: ID của ticket
            db: Database session (Support DB)

        Returns:
            Dict với overall_sentiment, message_sentiments, trend
        """
        if not db:
            return {"error": "Database session required"}

        from backend.models.ticket import Ticket, TicketMessage

        ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
        if not ticket:
            return {"error": f"Ticket {ticket_id} not found"}

        messages = db.query(TicketMessage).filter(
            TicketMessage.ticket_id == ticket_id
        ).order_by(TicketMessage.created_at).all()

        if not messages:
            return {
                "ticket_id": ticket_id,
                "ticket_number": ticket.ticket_number,
                "overall_sentiment": SentimentResult(
                    score=0.0,
                    label=SentimentLabel.NEUTRAL,
                    confidence=0.0,
                    text_preview=ticket.subject or ""
                ).to_dict(),
                "message_sentiments": [],
                "trend": "stable"
            }

        # Analyze each message
        message_sentiments = []
        for msg in messages:
            content = msg.message or ""
            if content.strip():
                result = self.analyze_text(content)
                message_sentiments.append({
                    "message_id": msg.id,
                    "is_staff": bool(msg.is_staff),
                    "sentiment": result.to_dict()
                })

        # Calculate overall sentiment (weighted by customer messages)
        customer_sentiments = [
            ms["sentiment"]["score"]
            for ms in message_sentiments
            if not ms["is_staff"]
        ]

        if customer_sentiments:
            overall_score = sum(customer_sentiments) / len(customer_sentiments)
        else:
            overall_score = 0.0

        overall_label = self._score_to_label(overall_score)
        trend = self._detect_trend(customer_sentiments)

        # Update ticket sentiment fields
        try:
            ticket.sentiment_score = overall_score
            ticket.sentiment_label = overall_label.value
            db.commit()
        except Exception:
            db.rollback()

        return {
            "ticket_id": ticket_id,
            "ticket_number": ticket.ticket_number,
            "overall_sentiment": {
                "score": round(overall_score, 4),
                "label": overall_label.value,
                "confidence": 0.8
            },
            "message_sentiments": message_sentiments,
            "trend": trend,
            "message_count": len(messages),
            "customer_message_count": len(customer_sentiments)
        }

    def analyze_conversation(
        self,
        conversation_id: str,
        db=None
    ) -> Dict[str, Any]:
        """
        Phân tích cảm xúc cuộc hội thoại.

        Args:
            conversation_id: ID của conversation
            db: Database session

        Returns:
            Dict với overall_sentiment, message_sentiments, trend
        """
        if not db:
            return {"error": "Database session required"}

        from backend.models.conversation import ConversationMessage

        messages = db.query(ConversationMessage).filter(
            ConversationMessage.conversation_id == conversation_id
        ).order_by(ConversationMessage.created_at).all()

        if not messages:
            return {
                "conversation_id": conversation_id,
                "overall_sentiment": {
                    "score": 0.0,
                    "label": "NEUTRAL",
                    "confidence": 0.0
                },
                "message_sentiments": [],
                "trend": "stable"
            }

        # Analyze each user message
        message_sentiments = []
        user_scores = []

        for msg in messages:
            role = getattr(msg, "role", "user")
            content = getattr(msg, "content", "") or ""
            if content.strip():
                result = self.analyze_text(content)
                msg_data = {
                    "message_id": msg.id,
                    "role": role,
                    "sentiment": result.to_dict()
                }
                message_sentiments.append(msg_data)
                if role == "user":
                    user_scores.append(result.score)

        overall_score = sum(user_scores) / len(user_scores) if user_scores else 0.0
        trend = self._detect_trend(user_scores)

        return {
            "conversation_id": conversation_id,
            "overall_sentiment": {
                "score": round(overall_score, 4),
                "label": self._score_to_label(overall_score).value,
                "confidence": 0.8
            },
            "message_sentiments": message_sentiments,
            "trend": trend,
            "message_count": len(messages),
            "user_message_count": len(user_scores)
        }

    def batch_analyze(self, texts: List[str]) -> List[SentimentResult]:
        """
        Phân tích cảm xúc hàng loạt.

        Args:
            texts: Danh sách text cần phân tích

        Returns:
            List[SentimentResult]
        """
        return [self.analyze_text(text) for text in texts]

    # ─── LLM Analysis ───────────────────────────────────────────

    def _analyze_with_llm(self, text: str) -> SentimentResult:
        """Phân tích cảm xúc bằng LLM"""
        prompt = f"""Phân tích cảm xúc của đoạn text khách hàng sau.

TEXT:
\"\"\"{text}\"\"\"

Trả lời CHÍNH XÁC theo JSON format sau (không thêm bất kỳ text nào khác):
{{
  "score": <float từ -1.0 đến 1.0>,
  "label": "<POSITIVE hoặc NEUTRAL hoặc NEGATIVE>",
  "confidence": <float từ 0.0 đến 1.0>,
  "emotions": {{
    "joy": <float 0-1>,
    "anger": <float 0-1>,
    "sadness": <float 0-1>,
    "surprise": <float 0-1>,
    "fear": <float 0-1>
  }}
}}

Quy tắc:
- score: -1.0 = rất tiêu cực, 0.0 = trung lập, 1.0 = rất tích cực
- label: POSITIVE (score > 0.2), NEUTRAL (-0.2 <= score <= 0.2), NEGATIVE (score < -0.2)
- confidence: Độ tin cậy của phân tích
- emotions: Phân bố cảm xúc chi tiết (tổng không cần = 1)
"""
        try:
            if self.llm_provider == "gemini":
                response = self.llm_client.models.generate_content(
                    model=ai_config.gemini_model,
                    contents=prompt
                )
                raw = (response.text or "").strip()

            elif self.llm_provider == "openai":
                response = self.llm_client.chat.completions.create(
                    model=ai_config.openai_model,
                    messages=[
                        {
                            "role": "system",
                            "content": "Bạn là chuyên gia phân tích cảm xúc. Chỉ trả lời JSON."
                        },
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=256,
                    temperature=0.1
                )
                raw = response.choices[0].message.content.strip()
            else:
                return self._analyze_rule_based(text)

            return self._parse_llm_response(raw, text)

        except Exception as e:
            print(f"[SentimentAnalyzer] LLM error, falling back to rules: {e}")
            return self._analyze_rule_based(text)

    def _parse_llm_response(self, raw: str, original_text: str) -> SentimentResult:
        """Parse JSON response from LLM"""
        try:
            # Extract JSON from possible markdown code block
            json_str = raw
            if "```" in raw:
                match = re.search(r"```(?:json)?\s*([\s\S]*?)```", raw)
                if match:
                    json_str = match.group(1).strip()

            data = json.loads(json_str)

            score = float(data.get("score", 0.0))
            score = max(-1.0, min(1.0, score))

            label_str = data.get("label", "NEUTRAL").upper()
            try:
                label = SentimentLabel(label_str)
            except ValueError:
                label = self._score_to_label(score)

            confidence = float(data.get("confidence", 0.8))
            confidence = max(0.0, min(1.0, confidence))

            emotions = {}
            raw_emotions = data.get("emotions", {})
            for key in ["joy", "anger", "sadness", "surprise", "fear"]:
                val = raw_emotions.get(key, 0.0)
                emotions[key] = max(0.0, min(1.0, float(val)))

            return SentimentResult(
                score=score,
                label=label,
                confidence=confidence,
                emotions=emotions,
                provider=self.llm_provider or "llm",
                text_preview=original_text[:100]
            )

        except (json.JSONDecodeError, ValueError, TypeError) as e:
            print(f"[SentimentAnalyzer] JSON parse error: {e}, raw: {raw[:200]}")
            return self._analyze_rule_based(original_text)

    # ─── Rule-based Analysis ─────────────────────────────────────

    def _analyze_rule_based(self, text: str) -> SentimentResult:
        """
        Rule-based sentiment analysis (offline fallback).
        Sử dụng lexicon tiếng Việt + English keywords.
        """
        text_lower = text.lower()
        words = re.findall(r'\w+', text_lower)

        pos_count = 0
        neg_count = 0
        has_negator = False
        intensifier_boost = 1.0

        # Check for negation in sentence
        for negator in self._NEGATORS:
            if negator in text_lower:
                has_negator = True
                break

        # Check for intensifiers
        for intensifier in self._INTENSIFIERS:
            if intensifier in text_lower:
                intensifier_boost = 1.3
                break

        # Count positive keywords
        for kw in self._POSITIVE_KEYWORDS:
            if kw in text_lower:
                pos_count += 1

        # Count negative keywords
        for kw in self._NEGATIVE_KEYWORDS:
            if kw in text_lower:
                neg_count += 1

        # If negator present, swap polarity
        if has_negator:
            pos_count, neg_count = neg_count, pos_count

        # Calculate score
        total = pos_count + neg_count
        if total == 0:
            score = 0.0
            confidence = 0.4
        else:
            raw_score = (pos_count - neg_count) / total
            score = max(-1.0, min(1.0, raw_score * intensifier_boost))
            confidence = min(0.9, 0.5 + (total * 0.05))

        # Emotions estimation
        emotions = {
            "joy": max(0.0, score) * 0.8 if score > 0 else 0.0,
            "anger": abs(min(0.0, score)) * 0.6 if score < -0.3 else 0.0,
            "sadness": abs(min(0.0, score)) * 0.4 if score < -0.1 else 0.0,
            "surprise": 0.1 if "!" in text else 0.0,
            "fear": 0.0
        }

        return SentimentResult(
            score=round(score, 4),
            label=self._score_to_label(score),
            confidence=round(confidence, 4),
            emotions=emotions,
            provider="rule_based",
            text_preview=text[:100]
        )

    # ─── Helpers ─────────────────────────────────────────────────

    @staticmethod
    def _score_to_label(score: float) -> SentimentLabel:
        """Convert score to label"""
        if score > 0.2:
            return SentimentLabel.POSITIVE
        elif score < -0.2:
            return SentimentLabel.NEGATIVE
        return SentimentLabel.NEUTRAL

    @staticmethod
    def _detect_trend(scores: List[float]) -> str:
        """
        Detect sentiment trend from ordered scores.

        Returns: 'improving', 'declining', 'stable'
        """
        if len(scores) < 2:
            return "stable"

        # Compare first half vs second half
        mid = len(scores) // 2
        first_half = sum(scores[:mid]) / mid if mid > 0 else 0
        second_half = sum(scores[mid:]) / (len(scores) - mid) if (len(scores) - mid) > 0 else 0

        diff = second_half - first_half
        if diff > 0.15:
            return "improving"
        elif diff < -0.15:
            return "declining"
        return "stable"
