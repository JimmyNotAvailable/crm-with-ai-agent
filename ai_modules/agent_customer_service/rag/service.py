"""
RAG Service - Main service for RAG-based Q&A
Tích hợp retriever và LLM để trả lời câu hỏi
"""
from typing import Dict, Any, Optional, List
import os
import re
from pathlib import Path

from ai_modules.core.config import ai_config
from .retriever import PolicyRetriever, ProductRetriever, DEFAULT_CHROMA_PATH


class RAGService:
    """
    RAG Service cho Customer Service Agent
    
    Chức năng:
    - Retrieve thông tin từ Policy/FAQ
    - Retrieve thông tin sản phẩm
    - Generate câu trả lời với LLM
    """
    
    def __init__(self, chroma_path: Optional[str] = None):
        # Use default chroma path from retriever module if not specified
        self.chroma_path = chroma_path or DEFAULT_CHROMA_PATH
        self.demo_mode = ai_config.demo_mode
        
        # Initialize retrievers
        self.policy_retriever = PolicyRetriever(self.chroma_path)
        self.product_retriever = ProductRetriever(self.chroma_path)
        
        # Initialize LLM client
        self._init_llm_client()
    
    def _init_llm_client(self):
        """Initialize LLM client (Gemini or OpenAI)"""
        self.llm_client = None
        self.llm_provider = None
        
        if self.demo_mode:
            return
        
        # Try Gemini first
        if ai_config.gemini_api_key:
            try:
                from google import genai
                self.llm_client = genai.Client(api_key=ai_config.gemini_api_key)
                self.llm_provider = "gemini"
                return
            except ImportError:
                pass
        
        # Fallback to OpenAI
        if ai_config.openai_api_key:
            try:
                from openai import OpenAI
                self.llm_client = OpenAI(api_key=ai_config.openai_api_key)
                self.llm_provider = "openai"
            except ImportError:
                pass
    
    def query(
        self,
        question: str,
        category: Optional[str] = None,
        top_k_policy: int = 4,
        top_k_product: int = 6
    ) -> Dict[str, Any]:
        """
        Query RAG pipeline
        
        Args:
            question: Câu hỏi của khách hàng
            category: Filter theo category sản phẩm (optional)
            top_k_policy: Số lượng policy docs để retrieve
            top_k_product: Số lượng product docs để retrieve
            
        Returns:
            Dict với answer và sources
        """
        # Retrieve relevant documents
        policy_docs = self.policy_retriever.retrieve(
            query=question,
            top_k=top_k_policy
        )
        
        product_docs = self.product_retriever.retrieve(
            query=question,
            category=category,
            top_k=top_k_product
        )
        
        if not policy_docs and not product_docs:
            return {
                "answer": "Hiện tại hệ thống chưa tìm thấy thông tin phù hợp để tư vấn cho yêu cầu này.",
                "sources": [],
                "confidence": 0.0
            }
        
        # Build context
        context = self._build_context(policy_docs, product_docs)
        
        # Generate answer
        if self.demo_mode or not self.llm_client:
            answer = self._generate_mock_answer(question, policy_docs, product_docs)
        else:
            answer = self._generate_llm_answer(question, context)
        
        # Build sources
        sources = self._build_sources(policy_docs, product_docs)
        
        return {
            "answer": answer,
            "sources": sources,
            "confidence": self._calculate_confidence(policy_docs, product_docs)
        }
    
    def compare_products(
        self,
        query: str,
        product_names: List[str],
        category: Optional[str] = None,
        top_k: int = 6
    ) -> Dict[str, Any]:
        """
        So sánh nhiều sản phẩm dựa trên query và tên sản phẩm.
        
        Args:
            query: Câu hỏi so sánh của khách hàng
            product_names: Danh sách tên sản phẩm cần so sánh
            category: Filter theo category (optional)
            top_k: Số sản phẩm tối đa để retrieve mỗi query
            
        Returns:
            Dict với comparison, products, comparison_table
        """
        all_products = []
        
        # Retrieve products cho mỗi tên sản phẩm
        for name in product_names:
            docs = self.product_retriever.retrieve(
                query=name,
                category=category,
                top_k=top_k // len(product_names) + 1 if product_names else top_k
            )
            for doc in docs:
                product_info = self._parse_product_from_doc(doc)
                if product_info and product_info not in all_products:
                    all_products.append(product_info)
        
        # Nếu chưa đủ sản phẩm, thử query chung
        if len(all_products) < 2:
            docs = self.product_retriever.retrieve(
                query=query,
                category=category,
                top_k=top_k
            )
            for doc in docs:
                product_info = self._parse_product_from_doc(doc)
                if product_info and product_info not in all_products:
                    all_products.append(product_info)
        
        if len(all_products) < 2:
            return {
                "comparison": "Không tìm đủ sản phẩm để so sánh.",
                "products": all_products,
                "comparison_table": None,
                "confidence": 0.0
            }
        
        # Limit to top products
        products_to_compare = all_products[:5]
        
        # Build comparison table
        comparison_table = self._build_comparison_table(products_to_compare)
        
        # Generate comparison text
        if self.demo_mode or not self.llm_client:
            comparison = self._generate_mock_comparison(products_to_compare, comparison_table)
        else:
            comparison = self._generate_llm_comparison(query, products_to_compare)
        
        return {
            "comparison": comparison,
            "products": products_to_compare,
            "comparison_table": comparison_table,
            "confidence": 0.85
        }
    
    def _parse_product_from_doc(self, doc: Dict) -> Optional[Dict]:
        """Parse product info from retrieved document"""
        content = doc.get("content", "")
        metadata = doc.get("metadata", {})
        
        # Try to extract structured info from content
        product = {
            "id": metadata.get("product_id") or metadata.get("id"),
            "name": metadata.get("name", ""),
            "price": metadata.get("price", 0),
            "category": metadata.get("category", ""),
            "specs": {},
            "description": "",
            "distance": doc.get("distance", 0)
        }
        
        # Parse content for more details
        lines = content.split("\n")
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Extract name if not in metadata
            if not product["name"] and ("tên" in line.lower() or line.startswith("**")):
                # Clean markdown
                name = re.sub(r'\*+', '', line).strip()
                name = re.sub(r'^(tên|sản phẩm)[:\s]*', '', name, flags=re.IGNORECASE).strip()
                if name:
                    product["name"] = name
            
            # Extract price
            if "giá" in line.lower() or "price" in line.lower():
                price_match = re.search(r'[\d,.]+', line.replace('.', '').replace(',', ''))
                if price_match:
                    try:
                        product["price"] = float(price_match.group())
                    except ValueError:
                        pass
            
            # Extract specs (key: value patterns)
            if ":" in line:
                parts = line.split(":", 1)
                if len(parts) == 2:
                    key = parts[0].strip().lower()
                    value = parts[1].strip()
                    if key and value and len(key) < 30:
                        product["specs"][key] = value
        
        # Use content as description if no structured data
        if not product["name"]:
            product["name"] = content[:50] + "..." if len(content) > 50 else content
        
        product["description"] = content[:200]
        
        return product if product.get("name") else None
    
    def _build_comparison_table(self, products: List[Dict]) -> Dict[str, List]:
        """Build comparison table from products"""
        if not products:
            return {}
        
        # Collect all spec keys
        all_specs = set()
        for p in products:
            all_specs.update(p.get("specs", {}).keys())
        
        # Common comparison attributes
        table = {
            "products": [p.get("name", "N/A") for p in products],
            "prices": [p.get("price", 0) for p in products],
            "categories": [p.get("category", "N/A") for p in products],
        }
        
        # Add specs to table
        for spec in all_specs:
            table[spec] = [p.get("specs", {}).get(spec, "N/A") for p in products]
        
        return table
    
    def _generate_llm_comparison(self, query: str, products: List[Dict]) -> str:
        """Generate comparison using LLM"""
        products_text = []
        for i, p in enumerate(products, 1):
            specs_text = "\n".join([f"  - {k}: {v}" for k, v in p.get("specs", {}).items()])
            products_text.append(f"""
SẢN PHẨM {i}: {p.get('name', 'N/A')}
- Giá: {p.get('price', 0):,.0f} VNĐ
- Danh mục: {p.get('category', 'N/A')}
{specs_text}
- Mô tả: {p.get('description', '')[:100]}
""")
        
        prompt = f"""
Bạn là chuyên viên tư vấn mua hàng. Hãy so sánh các sản phẩm sau để giúp khách hàng lựa chọn.

CÂU HỎI KHÁCH HÀNG:
{query}

THÔNG TIN SẢN PHẨM:
{''.join(products_text)}

YÊU CẦU:
1. So sánh các điểm giống và khác nhau chính
2. Nêu ưu/nhược điểm mỗi sản phẩm
3. Đưa ra gợi ý phù hợp với nhu cầu trong câu hỏi
4. Trình bày dễ đọc với bullet points
5. Trả lời thân thiện, chuyên nghiệp

SO SÁNH:
"""
        
        try:
            if self.llm_provider == "gemini":
                response = self.llm_client.models.generate_content(
                    model=ai_config.gemini_model,
                    contents=prompt
                )
                return (response.text or "").strip()
            
            elif self.llm_provider == "openai":
                response = self.llm_client.chat.completions.create(
                    model=ai_config.openai_model,
                    messages=[
                        {"role": "system", "content": "Bạn là chuyên viên tư vấn mua hàng chuyên nghiệp."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=800,
                    temperature=0.7
                )
                return response.choices[0].message.content.strip()
            
        except Exception as e:
            return self._generate_mock_comparison(products, None)
        
        return self._generate_mock_comparison(products, None)
    
    def _generate_mock_comparison(
        self, 
        products: List[Dict], 
        table: Optional[Dict]
    ) -> str:
        """Generate mock comparison for demo mode"""
        lines = ["**SO SÁNH SẢN PHẨM**\n"]
        
        # Product summaries
        for i, p in enumerate(products, 1):
            lines.append(f"### {i}. {p.get('name', 'N/A')}")
            lines.append(f"**Giá:** {p.get('price', 0):,.0f} VNĐ")
            lines.append(f"**Danh mục:** {p.get('category', 'N/A')}")
            
            # Specs
            specs = p.get("specs", {})
            if specs:
                lines.append("**Thông số:**")
                for k, v in list(specs.items())[:5]:
                    lines.append(f"  - {k}: {v}")
            lines.append("")
        
        # Comparison summary
        if len(products) >= 2:
            lines.append("---")
            lines.append("### TÓM TẮT SO SÁNH\n")
            
            # Price comparison
            prices = [(p.get("name", "")[:20], p.get("price", 0)) for p in products]
            sorted_prices = sorted(prices, key=lambda x: x[1])
            
            lines.append("**Giá cả:**")
            lines.append(f"  - Rẻ nhất: {sorted_prices[0][0]} ({sorted_prices[0][1]:,.0f}₫)")
            lines.append(f"  - Đắt nhất: {sorted_prices[-1][0]} ({sorted_prices[-1][1]:,.0f}₫)")
            lines.append("")
            
            lines.append("**Gợi ý:**")
            lines.append(f"  - Nếu ưu tiên giá: Chọn **{sorted_prices[0][0]}**")
            lines.append(f"  - Nếu ưu tiên tính năng cao cấp: Xem xét **{sorted_prices[-1][0]}**")
        
        lines.append("\n*Nhấn nút bên dưới để đặt hàng hoặc xem chi tiết.*")
        
        return "\n".join(lines)
    
    def _build_context(
        self, 
        policy_docs: List[Dict], 
        product_docs: List[Dict]
    ) -> str:
        """Build context string from retrieved documents"""
        context_blocks = []
        
        if product_docs:
            context_blocks.append("### THÔNG TIN SẢN PHẨM")
            for i, d in enumerate(product_docs, 1):
                context_blocks.append(f"[PRODUCT {i}] {d['content']}")
        
        if policy_docs:
            context_blocks.append("### CHÍNH SÁCH LIÊN QUAN")
            for i, d in enumerate(policy_docs, 1):
                context_blocks.append(f"[POLICY {i}] {d['content']}")
        
        return "\n\n".join(context_blocks)
    
    def _generate_llm_answer(self, question: str, context: str) -> str:
        """Generate answer using LLM"""
        prompt = f"""
Bạn là chuyên viên tư vấn mua hàng chuyên nghiệp.

NHIỆM VỤ:
- Trả lời câu hỏi của khách hàng dựa HOÀN TOÀN vào dữ liệu được cung cấp.
- KHÔNG bịa thông tin, KHÔNG dùng kiến thức ngoài CONTEXT.
- Trả lời thân thiện, chuyên nghiệp.

CONTEXT:
{context}

CÂU HỎI KHÁCH HÀNG:
{question}

TRẢ LỜI:
"""
        
        try:
            if self.llm_provider == "gemini":
                response = self.llm_client.models.generate_content(
                    model=ai_config.gemini_model,
                    contents=prompt
                )
                return (response.text or "").strip()
            
            elif self.llm_provider == "openai":
                response = self.llm_client.chat.completions.create(
                    model=ai_config.openai_model,
                    messages=[
                        {"role": "system", "content": "Bạn là chuyên viên tư vấn mua hàng chuyên nghiệp."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=512,
                    temperature=0.7
                )
                return response.choices[0].message.content.strip()
            
        except Exception as e:
            return f"Xin lỗi, hệ thống đang gặp sự cố. Vui lòng thử lại sau. ({str(e)})"
        
        return "Không thể tạo câu trả lời."
    
    def _generate_mock_answer(
        self, 
        question: str, 
        policy_docs: List[Dict], 
        product_docs: List[Dict]
    ) -> str:
        """Generate mock answer for demo mode"""
        lines = ["**[DEMO MODE]**\n"]
        
        if product_docs:
            lines.append(f"Tìm thấy {len(product_docs)} sản phẩm liên quan:")
            for doc in product_docs[:3]:
                content_preview = doc.get('content', '')[:100]
                lines.append(f"  - {content_preview}...")
            lines.append("")
        
        if policy_docs:
            lines.append(f"Tìm thấy {len(policy_docs)} chính sách liên quan:")
            for doc in policy_docs[:2]:
                content_preview = doc.get('content', '')[:100]
                lines.append(f"  - {content_preview}...")
        
        lines.append("\n*Đây là phản hồi demo. Production sẽ dùng Gemini/OpenAI.*")
        
        return "\n".join(lines)
    
    def _build_sources(
        self, 
        policy_docs: List[Dict], 
        product_docs: List[Dict]
    ) -> List[Dict[str, Any]]:
        """Build sources list from retrieved documents"""
        sources = []
        
        for d in product_docs + policy_docs:
            sources.append({
                "type": d.get("metadata", {}).get("type", "unknown"),
                "distance": round(d.get("distance", 0), 4),
                "meta": d.get("metadata", {})
            })
        
        return sources
    
    def _calculate_confidence(
        self, 
        policy_docs: List[Dict], 
        product_docs: List[Dict]
    ) -> float:
        """Calculate confidence score based on retrieved documents"""
        if not policy_docs and not product_docs:
            return 0.0
        
        all_docs = policy_docs + product_docs
        avg_distance = sum(d.get("distance", 1.0) for d in all_docs) / len(all_docs)
        
        # Convert distance to confidence (lower distance = higher confidence)
        confidence = max(0.0, 1.0 - avg_distance)
        return round(confidence, 2)
