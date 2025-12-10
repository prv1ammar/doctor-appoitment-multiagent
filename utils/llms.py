import os
from dotenv import load_dotenv

load_dotenv()

class LLMModel:
    def __init__(self, model_name="llama-3.1-8b-instant"):
        if not model_name:
            raise ValueError("Model is not defined.")
        
        self.model_name = model_name
        self.api_key = os.getenv("GROQ_API_KEY")
        
        # Try to use Groq if API key is available
        if self.api_key:
            try:
                from langchain_groq import ChatGroq
                self.llm = ChatGroq(
                    model=self.model_name,
                    api_key=self.api_key,
                    temperature=0.7,
                    max_tokens=None,  
                    timeout=15.0,
                    max_retries=2
                )
                self.using_mock = False
                print("INFO: Using Groq LLM")
            except ImportError:
                print("WARNING: langchain-groq not installed, using mock LLM")
                self.llm = self._create_mock_llm()
                self.using_mock = True
        else:
            print("WARNING: GROQ_API_KEY not found, using mock LLM for testing")
            self.llm = self._create_mock_llm()
            self.using_mock = True
        
    def _create_mock_llm(self):
        """Create a mock LLM for testing when Groq is not available."""
        try:
            # Try to use FakeListLLM which is designed for testing
            from langchain_community.llms.fake import FakeListLLM
            
            # Create responses for common queries
            responses = [
                # For greetings
                "Hello! How can I help you today?",
                # For appointment queries
                "I can help you with appointments. Please provide your patient ID, preferred date, and doctor name.",
                # For availability queries  
                "I can check doctor availability. Please specify which doctor and date you're interested in.",
                # For patient info queries
                "I can help with patient information. Please provide your patient ID.",
                # For FAQ queries
                "We offer dental services including orthodontics, prosthetics, and periodontology.",
                # Default response
                "I'm here to help with doctor appointments. You can ask about availability, book appointments, or manage patient information."
            ]
            
            # Create a FakeListLLM that cycles through responses
            mock_llm = FakeListLLM(responses=responses)
            
            # Add _llm_type attribute for detection
            mock_llm._llm_type = "mock"
            
            # Add with_structured_output method
            def with_structured_output(schema, **kwargs):
                # Return a callable that returns a mock structured output
                def mock_structured_invoker(messages):
                    # Create a mock response that matches the Router schema
                    class MockResponse:
                        def __init__(self):
                            self.next = "faq_sup_agent"
                            self.reasoning = "Mock LLM routing"
                    
                    return MockResponse()
                
                # Return an object that has an invoke method
                class MockStructuredLLM:
                    def invoke(self, messages):
                        return mock_structured_invoker(messages)
                
                return MockStructuredLLM()
            
            mock_llm.with_structured_output = with_structured_output
            
            return mock_llm
            
        except ImportError:
            # Fallback to a very simple mock if FakeListLLM is not available
            print("WARNING: langchain_community not available, using simple mock")
            from langchain_core.language_models import BaseLLM
            from langchain_core.outputs import LLMResult, Generation
            from typing import Any, List, Optional
            
            class SimpleMockLLM(BaseLLM):
                @property
                def _llm_type(self) -> str:
                    return "mock"
                
                def _generate(
                    self,
                    prompts: List[str],
                    stop: Optional[List[str]] = None,
                    run_manager: Optional[Any] = None,
                    **kwargs: Any,
                ) -> LLMResult:
                    responses = []
                    for prompt in prompts:
                        prompt_lower = prompt.lower()
                        if "hello" in prompt_lower or "hi" in prompt_lower:
                            response = "Hello! How can I help you today?"
                        elif "appointment" in prompt_lower or "booking" in prompt_lower or "book" in prompt_lower:
                            response = "I can help you with appointments. Please provide your patient ID, preferred date, and doctor name."
                        elif "available" in prompt_lower or "availability" in prompt_lower:
                            response = "I can check doctor availability. Please specify which doctor and date you're interested in."
                        elif "patient" in prompt_lower or "info" in prompt_lower or "information" in prompt_lower:
                            response = "I can help with patient information. Please provide your patient ID."
                        elif "service" in prompt_lower or "faq" in prompt_lower or "what" in prompt_lower:
                            response = "We offer dental services including orthodontics, prosthetics, and periodontology."
                        else:
                            response = "I'm here to help with doctor appointments. You can ask about availability, book appointments, or manage patient information."
                        
                        responses.append(Generation(text=response))
                    
                    return LLMResult(generations=[responses])
                
                def _llm_dict(self) -> dict:
                    return {"_type": "mock"}
                
                def with_structured_output(self, schema, **kwargs):
                    def mock_structured_invoker(messages):
                        class MockResponse:
                            def __init__(self):
                                self.next = "faq_sup_agent"
                                self.reasoning = "Mock LLM routing"
                        
                        return MockResponse()
                    
                    class MockStructuredLLM:
                        def invoke(self, messages):
                            return mock_structured_invoker(messages)
                    
                    return MockStructuredLLM()
            
            return SimpleMockLLM()
        
    def get_model(self):
        return self.llm

if __name__ == "__main__":
    llm_instance = LLMModel()  
    llm_model = llm_instance.get_model()
    response = llm_model.invoke("Hi, how are you?")
    print(response.content)
