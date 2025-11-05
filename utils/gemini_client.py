import os
from dotenv import load_dotenv
import logging
from google import genai
from google.genai import types

load_dotenv()

class GeminiClient:
    """Client for interacting with Gemini AI models"""
    
    def __init__(self):
        """Initialize the Gemini client"""
        self.__api_key = os.getenv("GEMINI_API_KEY")
        if not self.__api_key:
            raise ValueError("GEMINI_API_KEY environment variable is required")
        
        self.client = genai.Client(api_key=self.__api_key)
        self.model = "gemini-2.5-flash"  # Default model
    
    def analyze_image(self, image_path: str) -> str:
        """
        Analyze an image using Gemini Vision
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Image analysis description
        """
        try:
            with open(image_path, "rb") as f:
                image_bytes = f.read()
                
            response = self.client.models.generate_content(
                model="gemini-2.5-pro",  # Use pro model for vision
                contents=[
                    types.Part.from_bytes(
                        data=image_bytes,
                        mime_type="image/jpeg",
                    ),
                    "Analyze this image in detail. Describe its content, objects, people, text, " +
                    "context, and any other relevant information that could be useful for answering questions about it.",
                ],
            )
            
            return response.text if response.text else "Unable to analyze image"
            
        except Exception as e:
            raise Exception(f"Error analyzing image: {str(e)}")
    
    def analyze_video(self, video_path: str) -> str:
        """
        Analyze a video using Gemini
        
        Args:
            video_path: Path to the video file
            
        Returns:
            Video analysis description
        """
        try:
            with open(video_path, "rb") as f:
                video_bytes = f.read()
                
            response = self.client.models.generate_content(
                model="gemini-2.5-pro",  # Use pro model for video
                contents=[
                    types.Part.from_bytes(
                        data=video_bytes,
                        mime_type="video/mp4",
                    ),
                    "Analyze this video in detail. Describe its visual content, scenes, objects, people, " +
                    "actions, and any other relevant information that could be useful for answering questions about it.",
                ],
            )
            
            return response.text if response.text else "Unable to analyze video"
            
        except Exception as e:
            # Video analysis might not be available, so don't raise an exception
            logging.warning(f"Video analysis failed: {str(e)}")
            return ""
    
    def answer_question(self, question: str, context: str) -> str:
        """
        Generate an answer to a question based on provided context
        
        Args:
            question: User's question
            context: Relevant context from the knowledge base
            
        Returns:
            Generated answer
        """
        try:
            prompt = f"""Based on the following context, answer the user's question. Be comprehensive but concise. 
If the context doesn't contain enough information to answer the question completely, say so and provide what information is available.

Context:
{context}

Question: {question}

Answer:"""

            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt
            )
            
            return response.text if response.text else "Unable to generate an answer"
            
        except Exception as e:
            raise Exception(f"Error generating answer: {str(e)}")
    
    def summarize_content(self, content: str) -> str:
        """
        Summarize content using Gemini
        
        Args:
            content: Content to summarize
            
        Returns:
            Content summary
        """
        try:
            prompt = f"Summarize the following content concisely while preserving key information:\n\n{content}"
            
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt
            )
            
            return response.text if response.text else "Unable to generate summary"
            
        except Exception as e:
            raise Exception(f"Error generating summary: {str(e)}")
'''if __name__ == "__main__":
    client = GeminiClient()
    summary = client.summarize_content("Gemini is a multimodal AI model developed by Google DeepMind.")
    print(summary)'''
