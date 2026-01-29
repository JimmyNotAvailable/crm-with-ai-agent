"""
RAG Pipeline Service
"""
from typing import List, Optional, Dict, Any
try:
    from langchain_text_splitters import CharacterTextSplitter
except ImportError:
    try:
        from langchain.text_splitter import CharacterTextSplitter
    except ImportError:
        # Fallback to simple text splitter
        class CharacterTextSplitter:
            def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 100):
                self.chunk_size = chunk_size
                self.chunk_overlap = chunk_overlap
            
            def split_text(self, text: str) -> List[str]:
                chunks = []
                start = 0
                while start < len(text):
                    end = start + self.chunk_size
                    chunks.append(text[start:end])
                    start = end - self.chunk_overlap
                return chunks

try:
    from langchain_openai import OpenAIEmbeddings
except ImportError:
    from langchain.embeddings import OpenAIEmbeddings

import chromadb
import os

class RAGPipeline:
    def __init__(self, persist_directory: str = "./chroma_db"):
        self.chroma_client = chromadb.PersistentClient(path=persist_directory)
        self.text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        self.embedding_model = OpenAIEmbeddings()
        self.collection = self.chroma_client.get_or_create_collection(name="documents")

    def upload_and_index(self, file_path: str, metadata: Optional[dict] = None) -> int:
        """
        Upload file, chunk, embed, and store vectors in ChromaDB
        """
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()
        chunks = self.text_splitter.split_text(text)
        embeddings = self.embedding_model.embed_documents(chunks)
        ids = [f"{os.path.basename(file_path)}_{i}" for i in range(len(chunks))]
        self.collection.add(
            documents=chunks,
            embeddings=embeddings,
            ids=ids,
            metadatas=[metadata or {} for _ in chunks]
        )
        return len(chunks)

    def query(self, query_text: str, top_k: int = 3) -> List[str]:
        """
        Query ChromaDB for relevant chunks
        """
        query_embedding = self.embedding_model.embed_query(query_text)
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )
        return results["documents"][0] if results["documents"] else []

    def generate_answer(self, query: str, top_k: int = 3, crm_context: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate answer from top-k relevant chunks using OpenAI ChatCompletion
        Can include CRM context (customer info, orders, tickets) for personalized answers
        Falls back to mock response in DEMO_MODE
        """
        chunks = self.query(query, top_k=top_k)
        if not chunks:
            return "Không tìm thấy thông tin liên quan trong tài liệu."
        
        context = "\n\n---\n\n".join(chunks)
        
        # Check demo mode
        demo_mode = os.getenv("DEMO_MODE", "false").lower() == "true"
        
        if demo_mode:
            # Mock LLM response for demo
            return self._generate_mock_answer(query, chunks, crm_context)
        
        # Build prompt with CRM context if available
        system_message = "Bạn là trợ lý AI chuyên nghiệp cho hệ thống CRM."
        
        prompt_parts = [f"Dưới đây là các đoạn tài liệu liên quan:\n\n{context}"]
        
        if crm_context:
            crm_info = []
            if "customer" in crm_context:
                customer = crm_context["customer"]
                crm_info.append(f"Thông tin khách hàng: {customer.get('full_name', 'N/A')} - Email: {customer.get('email', 'N/A')}")
            if "orders" in crm_context:
                orders_count = len(crm_context["orders"])
                crm_info.append(f"Số đơn hàng: {orders_count}")
            if "tickets" in crm_context:
                tickets_count = len(crm_context["tickets"])
                crm_info.append(f"Số ticket hỗ trợ: {tickets_count}")
            
            if crm_info:
                prompt_parts.insert(0, "Thông tin CRM:\n" + "\n".join(crm_info) + "\n")
        
        prompt_parts.append(f"\nCâu hỏi: {query}\n\nHãy trả lời ngắn gọn, chính xác, dựa trên thông tin trong tài liệu và CRM context.")
        prompt = "\n".join(prompt_parts)
        
        try:
            from openai import OpenAI
            import os
            client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=512,
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"[LỖI] Không thể sinh câu trả lời: {str(e)}"
    
    def query_crm_entities(self, db_session, user_id: int) -> Dict[str, Any]:
        """
        Query CRM entities for a specific user (customer info, orders, tickets)
        """
        from backend.models.user import User
        from backend.models.order import Order
        from backend.models.ticket import Ticket
        
        crm_context = {}
        
        # Get customer info
        user = db_session.query(User).filter(User.id == user_id).first()
        if user:
            crm_context["customer"] = {
                "full_name": user.full_name,
                "email": user.email,
                "phone": user.phone
            }
        
        # Get recent orders
        orders = db_session.query(Order).filter(Order.customer_id == user_id).order_by(Order.created_at.desc()).limit(5).all()
        crm_context["orders"] = [
            {
                "order_number": order.order_number,
                "status": order.status.value,
                "total_amount": float(order.total_amount)
            } for order in orders
        ]
        
        # Get recent tickets
        tickets = db_session.query(Ticket).filter(Ticket.customer_id == user_id).order_by(Ticket.created_at.desc()).limit(5).all()
        crm_context["tickets"] = [
            {
                "ticket_number": ticket.ticket_number,
                "subject": ticket.subject,
                "status": ticket.status.value
            } for ticket in tickets
        ]
        
        return crm_context
    
    def _generate_mock_answer(self, query: str, chunks: List[str], crm_context: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate mock LLM answer for demo mode (no OpenAI API needed)
        """
        # Simple rule-based response for demo
        answer_parts = ["🤖 [DEMO MODE - Mock AI Response]\n"]
        
        # Add CRM context if available
        if crm_context:
            if "customer" in crm_context:
                customer = crm_context["customer"]
                answer_parts.append(f"Xin chào {customer.get('full_name', 'Quý khách')}!\n")
            if "orders" in crm_context and crm_context["orders"]:
                orders_count = len(crm_context["orders"])
                answer_parts.append(f"Tôi thấy bạn có {orders_count} đơn hàng trong hệ thống.\n")
        
        # Summarize retrieved chunks
        answer_parts.append(f"Dựa trên tài liệu, tôi tìm thấy {len(chunks)} đoạn thông tin liên quan đến câu hỏi: '{query}'.\n")
        
        # Extract key info from first chunk
        if chunks:
            first_chunk = chunks[0][:300]  # First 300 chars
            answer_parts.append(f"\nThông tin chính:\n{first_chunk}...\n")
        
        # Add helpful note
        answer_parts.append("\n💡 Lưu ý: Đây là phản hồi mô phỏng cho mục đích demo. Trong môi trường production, hệ thống sẽ sử dụng OpenAI GPT để tạo câu trả lời thông minh hơn.")
        
        
        return "\n".join(answer_parts)
    
    def index_knowledge_article(
        self, 
        article_id: int, 
        title: str, 
        content: str, 
        category: str
    ) -> int:
        """
        Index a knowledge base article into ChromaDB for semantic search
        Returns number of chunks created
        """
        # Combine title and content for better context
        full_text = f"# {title}\n\nCategory: {category}\n\n{content}"
        
        # Split into chunks
        chunks = self.text_splitter.split_text(full_text)
        
        # Generate embeddings
        embeddings = self.embedding_model.embed_documents(chunks)
        
        # Create unique IDs for each chunk
        ids = [f"kb_{article_id}_chunk_{i}" for i in range(len(chunks))]
        
        # Prepare metadata for each chunk
        metadatas = [
            {
                "article_id": article_id,
                "title": title,
                "category": category,
                "chunk_index": i,
                "source_type": "knowledge_base"
            }
            for i in range(len(chunks))
        ]
        
        # Add to ChromaDB collection
        self.collection.add(
            documents=chunks,
            embeddings=embeddings,
            ids=ids,
            metadatas=metadatas
        )
        
        return len(chunks)


