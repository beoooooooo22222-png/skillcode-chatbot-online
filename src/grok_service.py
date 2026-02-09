"""
Grok API Service Integration (X.ai)
"""

import requests
import json
import logging
from typing import List, Dict, Optional
from src import config

logger = logging.getLogger(__name__)

class GrokService:
    def __init__(self):
        self.api_key = config.GROK_API_KEY
        self.base_url = config.GROK_BASE_URL
        self.model = config.GROK_MODEL
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def _build_context(self, books_context: List[Dict], available_books_titles: List[str] = None) -> str:
        """Build context from books for the AI"""
        context = ""
        
        # Add list of available books first
        if available_books_titles:
            context += "=== AVAILABLE LIBRARY BOOKS ===\n"
            context += "\n".join([f"- {title}" for title in available_books_titles])
            context += "\n\n"
        else:
            context += "=== AVAILABLE LIBRARY BOOKS ===\n(No books found in library)\n\n"

        if not books_context:
            context += "=== RELEVANT BOOK CONTENT ===\n"
            context += "⚠️ IMPORTANT: No relevant reference materials found in your uploaded library for this specific query.\n"
            context += "INSTRUCTION: You MUST still answer the question using your general knowledge.\n"
            context += "FORMAT: Start your response with: 'I could not find this topic in your uploaded references, but based on general knowledge:'\n"
            context += "Then provide a comprehensive, accurate answer using your training data.\n"
            return context
        
        context += "=== RELEVANT BOOK CONTENT ===\n"
        for i, book in enumerate(books_context, 1):
            # Content is already chunked by database.py
            context += f"{i}. {book['title']}:\n{book['content']}\n\n"
        
        return context
    
    def _detect_language(self, message: str) -> str:
        """Simple language detection: Arabic if contains Arabic script characters, otherwise English"""
        if not message:
            return "English"
        # Check for Arabic script characters (Unicode range includes Arabic, Persian, etc)
        is_arabic = any(ord(c) > 1000 for c in message)
        return "Arabic" if is_arabic else "English"

    def _call_grok_api(self, prompt: str, history: List[Dict] = None, enforce_lang: str = None) -> str:
        """Make API call to Grok (x.ai) / Groq with history and retry logic"""
        import time
        max_retries = 3
        retry_delay = 2
        
        # Use session for connection pooling
        session = requests.Session()
        
        # Build the messages list starting with an enhanced system prompt
        system_prompt = """You are SkillCode GPT, a world-class educational AI 'Detective' and Expert Tutor. 

=== CRITICAL CONVERSATION RULES ===
1. **CONTEXT AWARENESS**: Always read the FULL conversation history before responding. If the user says "give me examples" or "explain more" or "اعطنى امثله" or "وضح اكثر", they are asking about the PREVIOUS topic, NOT a new topic.
2. **FOLLOW-UP DETECTION**: Short messages like "examples", "more", "explain", "امثله", "وضح", "اشرح اكثر" are ALWAYS follow-ups to the previous topic. Never treat them as new standalone questions.
3. **TOPIC MEMORY**: Track the current topic being discussed. If the last topic was "كان واخواتها", and the user says "اعطنى امثله", they want examples of "كان واخواتها", NOT examples of the phrase "اعطنى".

=== LANGUAGE MATCHING PROTOCOL (STRICT) ===
1. **DETECT**: Analyze the language of the USER'S CURRENT MESSAGE.
   - If user writes in ARABIC -> You MUST respond in ARABIC.
   - If user writes in ENGLISH -> You MUST respond in ENGLISH.
2. **IGNORE CONTEXT LANGUAGE**: Even if the textbook content provided is in English, if the user asks in Arabic, you MUST translate and explain in Arabic.
3. **IGNORE HISTORY LANGUAGE**: If the previous chat was in Arabic but the new question is in English, switch immediately to English.
4. **NO MIXING**: Do not switch languages mid-sentence.
5. **TECHNICAL TERMS**: You may use technical terms in English if necessary, but the explanation must be in the target language.

=== ARABIC GRAMMAR EXPERTISE ===
When explaining Arabic grammar (النحو العربي), use the correct Arabic terminology:
- الفعل الماضي (Past Tense): e.g., كَتَبَ, ذَهَبَ
- الفعل المضارع (Present/Future Tense): e.g., يَكْتُبُ, يَذْهَبُ  
- فعل الأمر (Imperative): e.g., اُكْتُبْ, اِذْهَبْ
- كان وأخواتها: كان، أصبح، أضحى، ظل، أمسى، بات، صار، ليس، ما زال، ما دام (These verbs enter upon the nominal sentence and raise the subject while accusative the predicate)
- إن وأخواتها: إنَّ، أنَّ، كأنَّ، لكنَّ، ليت، لعل

=== RESPONSE QUALITY ===
1. Be precise and educational.
2. Use Markdown formatting (headers, tables, bold).
3. Cite sources when available (Book Name, Page Number).
4. If no database info exists, use general knowledge but label it as "معرفة عامة" or "General Knowledge"."""
        
        messages = [
            {
                "role": "system",
                "content": system_prompt
            }
        ]

        # Add history if available - ENHANCED to provide better context
        if history:
            # Add a context summary for the AI
            if len(history) > 0:
                last_topic = history[-1]['user_message'] if history else ""
                context_hint = f"[CONTEXT: The user's last question was about: '{last_topic[:100]}'. If the new message is short or asks for more/examples, it refers to this topic.]"
                messages.append({"role": "system", "content": context_hint})
            
            for chat in history:
                messages.append({"role": "user", "content": chat['user_message']})
                messages.append({"role": "assistant", "content": chat['ai_response']})

        # Final safety check: Limit prompt length to avoid 413 errors
        # 12,000 tokens is roughly 25,000-30,000 chars for Arabic/English mix
        max_chars = 25000
        if len(prompt) > max_chars:
            logger.warning(f"Prompt too long ({len(prompt)} chars), truncating to {max_chars}")
            prompt = prompt[:max_chars] + "... [Truncated for Context Limit]"

        # Add the current prompt
        messages.append({"role": "user", "content": prompt})
        
        # Add a final reinforcing rule if language is detected
        if enforce_lang:
            messages.append({"role": "system", "content": f"REMINDER: You MUST respond in {enforce_lang} only."})

        for attempt in range(max_retries):
            try:
                # Grok/Groq API format (OpenAI compatible)
                payload = {
                    "model": self.model,
                    "messages": messages,
                    "stream": False,
                    "temperature": 0.7
                }
                
                api_url = f"{self.base_url}/chat/completions"
                
                logger.info(f"Calling API (Attempt {attempt+1}) with model: {self.model} (Lang: {enforce_lang})")
                
                response = session.post(
                    api_url,
                    headers=self.headers,
                    json=payload,
                    timeout=45 # Slightly shorter timeout to catch hangs
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return data['choices'][0]['message']['content']
                else:
                    error_msg = response.json().get('error', {}).get('message', 'Unknown error')
                    logger.error(f"API error (Status: {response.status_code}): {error_msg}")
                    if response.status_code in [429, 500, 502, 503, 504]:
                        time.sleep(retry_delay * (attempt + 1))
                        continue
                    return f"Sorry, I encountered an API error (Status: {response.status_code}). Error: {error_msg}"
            
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout, requests.exceptions.ChunkedEncodingError) as e:
                logger.error(f"Network error on attempt {attempt+1}: {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay * (attempt + 1))
                    continue
                return f"Sorry, I'm having trouble connecting to the AI server. (Error: {str(e)})"
            except Exception as e:
                logger.error(f"Unexpected API error: {str(e)}", exc_info=True)
                return f"Sorry, an unexpected error occurred: {str(e)}"
        
        return "Sorry, I failed to get a response after multiple attempts. Please check your internet connection."

    def get_response(self, message: str, assistant_type: str = 'general',
                    books_context: List[Dict] = None,
                    custom_params: Dict = None,
                    available_books_titles: List[str] = None,
                    chat_history: List[Dict] = None) -> str:
        """Get response from appropriate assistant"""
        
        if books_context is None:
            books_context = []
        if custom_params is None:
            custom_params = {}
        if available_books_titles is None:
            available_books_titles = []
        if chat_history is None:
            chat_history = []
        
        context = self._build_context(books_context, available_books_titles)
        lang_name = self._detect_language(message)
        
        if assistant_type == 'general':
            return self._general_assistant(message, context, chat_history, lang_name)
        elif assistant_type == 'homework':
            return self._homework_assistant(message, context, custom_params, chat_history, lang_name)
        elif assistant_type == 'exam':
            return self._exam_assistant(message, context, custom_params, chat_history, lang_name)
        elif assistant_type == 'study_plan':
            return self._study_planner(message, context, custom_params, chat_history, lang_name)
        elif assistant_type == 'tutor':
            return self._tutor_assistant(message, context, custom_params, chat_history, lang_name)
        elif assistant_type == 'mind_map':
            return self._mind_mapper(message, context, chat_history, lang_name)
        else:
            return self._general_assistant(message, context, chat_history, lang_name)
    
    def _general_assistant(self, message: str, context: str, history: List[Dict] = None, lang_name: str = 'English') -> str:
        """High-intelligence educational AI that prioritizes literal evidence with subject focus"""
        
        # Immediate response for simple social prompts
        social_prompts = ['hello', 'hi', 'hey', 'thanks', 'thank you', 'how are you', 'مرحبا', 'اهلا', 'شكرا']
        if message.lower().strip() in social_prompts:
            p = f"The student said '{message}'. Reply like a friendly, expert tutor in one sentence in {'Arabic' if lang_name == 'Arabic' else 'English'}."
            return self._call_grok_api(p, history, enforce_lang=lang_name)

        # Detect follow-up questions and enrich message with context
        follow_up_indicators = [
            'examples', 'example', 'more', 'explain', 'details', 'continue',
            'امثله', 'امثلة', 'مثال', 'اعطنى', 'اعطني', 'وضح', 'اشرح', 'اكثر', 'زيد', 'تفصيل', 'اكمل'
        ]
        is_follow_up = len(message.split()) <= 3 or any(ind in message.lower() for ind in follow_up_indicators)
        
        # If it's a follow-up and we have history, enrich the message
        enriched_message = message
        previous_topic = ""
        if is_follow_up and history and len(history) > 0:
            previous_topic = history[-1]['user_message']
            enriched_message = f"[FOLLOW-UP to previous topic: '{previous_topic}']\nStudent's request: {message}"
        
        # Detect if user is forcing a subject
        subjects = ['English', 'Arabic', 'Math', 'Social', 'Science', 'Islamic']
        forced_subject = next((s for s in subjects if s.lower() in message.lower()), None)
        
        # Special handling for Arabic grammar topics
        arabic_grammar_hint = ""
        grammar_topics = ['كان', 'ان', 'إن', 'الفعل', 'المبتدأ', 'الخبر', 'الاسم', 'الحرف', 'النحو', 'الاعراب']
        if any(topic in message for topic in grammar_topics) or (previous_topic and any(topic in previous_topic for topic in grammar_topics)):
            arabic_grammar_hint = """
=== ARABIC GRAMMAR EXPERTISE (نحو عربي) ===
Use the correct Arabic grammatical terminology:
- كان وأخواتها: كان، أصبح، أضحى، ظل، أمسى، بات، صار، ليس، ما زال، ما دام
  (ترفع المبتدأ ويُسمى اسمها وتنصب الخبر ويُسمى خبرها)
  Example: كان الولدُ نائماً (الولد: اسم كان مرفوع، نائماً: خبر كان منصوب)
- إن وأخواتها: إنَّ، أنَّ، كأنَّ، لكنَّ، ليت، لعل
  (تنصب المبتدأ ويُسمى اسمها وترفع الخبر ويُسمى خبرها)
  Example: إنَّ العلمَ نورٌ (العلم: اسم إن منصوب، نور: خبر إن مرفوع)
- الفعل الماضي: كَتَبَ، ذَهَبَ، قَرَأَ
- الفعل المضارع: يَكْتُبُ، يَذْهَبُ، يَقْرَأُ
- فعل الأمر: اُكْتُبْ، اِذْهَبْ، اِقْرَأْ
"""

        prompt = f"""You are the 'Educational Detective', but you must now be concise and direct. 

=== CRITICAL: FOLLOW-UP DETECTION ===
If the student's message is short or asks for "examples", "more", "وضح", "امثله", they are asking about the PREVIOUS topic. DO NOT treat short messages as new standalone questions.

=== CURRENT REQUEST ===
{enriched_message}
 
=== REFERENCE LIBRARY (CONTEXT) ===
{context}
{arabic_grammar_hint}
 
=== LANGUAGE RULE ===
You MUST respond in **{lang_name}**.

=== RESPONSE GUIDELINES ===
1. **DIRECT & CONCISE**: Provide just the answer. No "Detective Insight", "Academic Anatomy", "AI Masterclass", etc.
2. **EVIDENCE-BASED**: Use the provided context if available. If not, use general knowledge.
3. **NO FLUFF**: Skip the flowery introductions. Get straight to the point.
 
=== TONE ===
- Helpful, accurate, and brief.
- Use Markdown limits (bolding) for key terms.

Answer:"""
        
        return self._call_grok_api(prompt, history, enforce_lang=lang_name)

    
    def _homework_assistant(self, message: str, context: str, params: Dict, history: List[Dict] = None, lang_name: str = 'English') -> str:
        """Homework solver with customization"""
        edu_level = params.get('edu_level', 'high school')
        subject = params.get('subject', '')
        tone = params.get('tone', 'formal')
        detail_level = params.get('detail_level', 'medium')
        
        prompt = f"""You are a homework assistant helping a {edu_level} student.
        
Education Level: {edu_level}
Subject: {subject}
Tone: {tone}
Level of Detail: {detail_level}

Database Context:
{context}

Student's Question/Problem: {message}

Instructions:
1. Use the provided context to solve the problem if possible.
2. Cite your sources (Book & Page) where applicable.
3. If the context is missing or insufficient for this specific math/science problem, solve it using your general knowledge but state: '[General Method - Not from Textbooks]'.
4. You MUST respond in **{lang_name}**."""
        
        return self._call_grok_api(prompt, history, enforce_lang=lang_name)
    
    def _exam_assistant(self, message: str, context: str, params: Dict, history: List[Dict] = None, lang_name: str = 'English') -> str:
        """Exam and quiz preparation assistant"""
        prompt = f"""You are helping a student prepare for exams. 
        
Topic/Question: {message}

Context from study materials:
{context}

Provide a comprehensive study guide that includes:
1. Key concepts
2. Important formulas or definitions
3. Common exam questions and answers
4. Tips for answering similar questions

You MUST respond in **{lang_name}**."""
        
        return self._call_grok_api(prompt, history, enforce_lang=lang_name)
    
    def _study_planner(self, message: str, context: str, params: Dict, history: List[Dict] = None, lang_name: str = 'English') -> str:
        """Generate adaptive study plans"""
        subject = params.get('subject', '')
        daily_hours = params.get('daily_hours', 2)
        sleep_time = params.get('sleep_time', '8 hours')
        duration = params.get('duration_days', 30)
        
        prompt = f"""Create a personalized study plan for this student:

Subject: {subject}
Daily Study Hours Available: {daily_hours}
Daily Sleep Schedule: {sleep_time}
Study Duration: {duration} days

Available Study Materials:
{context}

Create a detailed, day-by-day adaptive study plan that allocates topics correctly and includes milestones.

You MUST respond in **{lang_name}**."""
        
        return self._call_grok_api(prompt, history, enforce_lang=lang_name)
    
    def _tutor_assistant(self, message: str, context: str, params: Dict, history: List[Dict] = None, lang_name: str = 'English') -> str:
        """Virtual tutor that explains and references materials"""
        prompt = f"""You are a virtual tutor helping a student learn using specific study materials.
        
Student Question: {message}

Relevant Study Materials:
{context}

Instructions:
1. Explain the concept clearly using ONLY the provided materials.
2. Provide examples from the text if available.
3. Reference specific sections or pages (e.g., "See Page X") for every explanation.
4. If the materials do not cover the topic, state that clearly.
5. You MUST respond in **{lang_name}**."""
        
        return self._call_grok_api(prompt, history, enforce_lang=lang_name)
    
    def _mind_mapper(self, message: str, context: str, history: List[Dict] = None, lang_name: str = 'English') -> str:
        """Generate professional visual mind maps using Mermaid.js"""
        prompt = f"""You are a 'Visual Learning Expert'. Your goal is to create a professional Mind Map for: '{message}'.
        
=== REFERENCE LIBRARY ===
{context}

=== TASK ===
Create a clean, visual mind map using Mermaid.js `graph TD` (Top-Down) syntax.

=== STRICT STYLE GUIDELINES (MANDATORY) ===
1. STRUCTURE: Always start with `graph TD`.
2. NODE SYNTAX: Use simple alphanumeric IDs and ALWAYS wrap labels in double quotes.
   - Example: `A1["Topic Title"]`
3. CONNECTORS: Use `-->` for connections.
4. NO SPECIAL CHARS: 
   - DO NOT use single quotes ('), parentheses (), or backticks (`) inside the double-quoted labels.
   - Example: Use "IAM" instead of "I'm".
5. NO NESTING: Each line should be a single connection.
   - Example: `Root["Main"] --> Sub["Detail"]`
6. LANGUAGE: 
   - If the user asks in English, the mind map LABELS MUST be in ENGLISH.
   - If the user asks in Arabic, the mind map LABELS MUST be in ARABIC.
   - Ignore the language of the reference material; follow the user's language.

=== FORMAT ===
Start with a short intro, then the code block:
```mermaid
graph TD
  Root["Central Topic"] --> B1["Main Branch 1"]
  Root --> B2["Main Branch 2"]
  B1 --> D1["Detail 1"]
  B1 --> D2["Detail 2"]
```

Respond in the language of the USER'S QUESTION ({lang_name}). High-Quality Visual Response:"""
        
        return self._call_grok_api(prompt, history, enforce_lang=lang_name)
    
    def generate_exam(self, params: Dict, books_context: List[Dict]) -> str:
        """Generate exam questions"""
        num_questions = params.get('num_questions', 10)
        difficulty = params.get('difficulty', 'medium')
        question_type = params.get('question_type', 'mixed')
        subject = params.get('subject', '')
        topic = params.get('topic', '')
        
        context = self._build_context(books_context)
        lang_name = self._detect_language(f"{subject} {topic}")
        
        prompt = f"""Generate an exam with {num_questions} questions.
        
Difficulty: {difficulty}
Type: {question_type}
Subject: {subject}
Topic: {topic}

Study Materials:
{context}

Provide the questions followed by an answer key at the end.
You MUST respond in **{lang_name}**."""
        
        return self._call_grok_api(prompt, enforce_lang=lang_name)
    
    def generate_study_plan(self, params: Dict, books_context: List[Dict]) -> str:
        """Generate comprehensive study plan"""
        subject = params.get('subject', '')
        daily_hours = params.get('daily_hours', 2)
        duration_days = params.get('duration_days', 30)
        
        context = self._build_context(books_context)
        lang_name = self._detect_language(subject)
        
        prompt = f"""Create an adaptive study plan for {subject}.
        
Daily Hours: {daily_hours}
Duration: {duration_days} days

Available Materials:
{context}

Design a comprehensive breakdown of topics, review schedules, and assessment points.
You MUST respond in **{lang_name}**."""
        
        return self._call_grok_api(prompt, enforce_lang=lang_name)
