from django.conf import settings
import os
import openai

class AIContentService:
    def __init__(self):
        # TODO: Initialize OpenAI API KEY here
        openai.api_key = os.getenv("OPENAI_API_KEY")
        
    def generate_topic_suggestions(self, user_interests, trending_topics):
        prompt = f"""
        Generate topic suggestions based on user interests: {user_interests} and trending topics: {trending_topics}.
        Suggest 5 relevant blog post topics for the user.
        """
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ]
        )
        
        return response.choices[0].message.content
    
    def analyze_content(self, content):
        prompt = f"""
        Analyze the content and provide readability, SEO optimization, sentiment, key points, improvement suggestions and relevance scores.
        Content: {content}
        """
        
        response = openai.ChatCompletion.create(
            engine="gpt-3.5-turbo",
            message=[
                {"role": "system", "content": "You are a content strategy expert."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=200
        )
        
        return response.choices[0].messages.content
    
    def improve_content(self, content, style_guide):
        prompt = f"""
        Improve the content based on the style guide: {style_guide}.
        Content: {content}
        """
        
        response = openai.ChatCompletion.create(
            model = "gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a content strategy expert."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=200
        )
        
        return response.choices[0].message.content