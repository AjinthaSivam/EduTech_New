from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import QuestionRequestSerializer
import openai
from django.conf import settings
import json

class GenerateQuestionsView(APIView):
    def post(self, request):
        serializer = QuestionRequestSerializer(data=request.data)
        if serializer.is_valid():
            category = serializer.validated_data.get('category', '')
            difficulty = serializer.validated_data.get('difficulty', '')

            questions = self.generate_questions(category, difficulty)
            return Response({'questions': questions}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def generate_questions(self, category, difficulty):
        openai.api_key = settings.OPENAI_API_KEY
        prompt = f"Generate 5 English MCQ questions with category '{category}' and difficulty '{difficulty}' with 4 options each. Format the response as JSON with fields 'question', 'options', and write the 'answer'."
        response = openai.Completion.create(
            engine="gpt-3.5-turbo-instruct",
            prompt=prompt,
            max_tokens=500,
            n=1,
            stop=None,
            # temperature=0.3
        )
        response_text = response.choices[0].text.strip()
        
        print("Raw response from OpenAI: ", response_text)
        
        questions = []
        
        question_blocks = response_text.split("\n\n")
        
        for block in question_blocks:
            lines = block.split("\n")
            
            if len(lines) < 3:
                continue
            
            question_line = lines[0].strip()
            options_lines = lines[1:-1]
            answer_line = lines[-1].strip()
            
            try:
                question_text = question_line.split(":", 1)[1].strip()
            except IndexError:
                continue
            
            options = {}
            
            i = 0
            
            for i, opt in enumerate(options_lines):
                try:
                    opt_cleaned = opt.strip().split(") ", 1)
                    if len(opt_cleaned) == 2: 
                        option_label = chr(64 + i)
                        option_text = opt_cleaned[1].strip()
                        options[f"Option {option_label}"] = option_text
                    else:
                        continue
                    
                except ValueError:
                    continue
                
            try:
                answer = answer_line.split(": ", 1)[1].strip()
            except IndexError:
                continue
            
            questions.append({
                "question": question_text,
                "options": options,
                "answer": answer
                
            })
            
            # answers.append({
            #     "question": question_text,
            #     "options": options,
            #     "answer": answer
            # })
                      
        return questions

