import os
import PyPDF2
import openai
import numpy as np
import faiss
import json
import pytz
from django.utils import timezone
from django.http import JsonResponse
from django.views import View
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .models import Chat, ChatHistory
from .serializers import ChatSerializer
from django.conf import settings

openai.api_key = settings.OPENAI_API_KEY

# Directory paths
input_directory = 'pdfs'  # Directory where your PDFs are stored
output_file_path = os.path.join(input_directory, 'ExtractedReference.txt')

# Ensure the directory exists
if not os.path.exists(input_directory):
    os.makedirs(input_directory)

# Function to convert PDF to text using PyPDF2
def convert_pdf_to_text(file_path):
    try:
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ''
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text
            return text
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return ''

# List all PDF files in the input directory
file_names = [f for f in os.listdir(input_directory) if f.endswith('.pdf')]

# Process and save the text output for each PDF file into a single text file
with open(output_file_path, 'w', encoding='utf-8') as output_file:
    for file_name in file_names:
        file_path = os.path.join(input_directory, file_name)
        text = convert_pdf_to_text(file_path)
        if text:
            output_file.write(f"--- Start of {file_name} ---\n")
            output_file.write(text)
            output_file.write(f"\n--- End of {file_name} ---\n\n")
            print(f"Processed {file_name} and appended to {output_file_path}")
        else:
            print(f"Skipping {file_name} due to errors.")

print(f"All files processed. Consolidated text saved to {output_file_path}")

# Load the consolidated text into memory
with open(output_file_path, 'r', encoding='utf-8') as file:
    dataset_text = file.read()

# Chunk the dataset into manageable parts
chunk_size = 2000  # Increase chunk size for better context
dataset_chunks = [dataset_text[i:i + chunk_size] for i in range(0, len(dataset_text), chunk_size)]

# Function to get embeddings
def get_embedding(text):
    return openai.Embedding.create(input=text, model="text-embedding-ada-002")['data'][0]['embedding']

# Get embeddings for each chunk
embeddings = [get_embedding(chunk) for chunk in dataset_chunks if chunk.strip()]

# Convert embeddings to a numpy array
embeddings_np = np.array(embeddings).astype("float32")

# Create a FAISS index if embeddings are not empty
index = None
if embeddings_np.size > 0:
    index = faiss.IndexFlatL2(embeddings_np.shape[1])
    index.add(embeddings_np)
else:
    print("Error: embeddings_np is empty. Ensure valid text was extracted from the PDFs.")

# Save the chunks and their embeddings
chunks_and_embeddings = list(zip(dataset_chunks, embeddings))

# Function to find the most relevant chunks based on the user query
def find_relevant_chunks(query, chunks_and_embeddings, index, top_k=5):
    try:
        if index is None:
            raise ValueError("Index is not initialized correctly.")
        
        query_embedding = get_embedding(query)
        _, I = index.search(np.array([query_embedding]).astype("float32"), top_k)
        return [chunks_and_embeddings[i][0] for i in I[0]]
    
    except Exception as e:
        print("An error occurred in find_relevant_chunks:", str(e))
        return []

# Define the conversation loop with the OpenAI assistant
print("Welcome! How can I assist you today?")
conversation_history = []

# State to track the current focus of the conversation
current_focus = None

def process_query(user_input, learner, chat):
    global conversation_history
    global current_focus
    try:
        # Append user input to conversation history
        conversation_history.append({"role": "user", "content": user_input})

        # Find relevant chunks from the dataset
        relevant_chunks = find_relevant_chunks(user_input, chunks_and_embeddings, index)
        if relevant_chunks:
            context_text = ' '.join(relevant_chunks[:5])  # Use top 5 relevant chunks, adjust as needed
        else:
            context_text = "No relevant information found in the provided reference material."

        # Use OpenAI API to get assistant's response
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an English Teaching Assistant. Guide students through questions by first offering options and checking their understanding of the basics before giving the answer. If they answer incorrectly, explain the concept before proceeding. Use very simple English. Don't use hard words. You may give options to select for their ease"},
                {"role": "system", "content": f"Reference Material: {context_text}"},
                *conversation_history
            ]
        )

        assistant_response = response['choices'][0]['message']['content'].strip()
        print("EduTech Assistant:", assistant_response)

        # Append assistant response to conversation history
        conversation_history.append({"role": "assistant", "content": assistant_response})

        ChatHistory.objects.create(
            chat=chat,
            message=user_input,
            response=assistant_response
        )

        return {
            'message': user_input,
            'response': assistant_response,
            'chat_id': chat.chat_id,
            'learner_id': learner.id
        }

    except Exception as e:
        print("An error occurred:", str(e))
        return "An error occurred. Please try again later."

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def chat_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_input = data.get('user_input', '')
            new_chat = data.get('new_chat', False)

            learner = request.user
            chat = None
            chat_id = data.get('chat_id')

            if not chat_id:
                chat = Chat.objects.create(
                    learner=learner,
                    chat_title=user_input,
                    chat_started_at=timezone.now().astimezone(pytz.timezone('Asia/Colombo')),
                    last_message_at=timezone.now().astimezone(pytz.timezone('Asia/Colombo'))
                )
            else:
                chat = Chat.objects.get(id=chat_id)

            response_data = process_query(user_input, learner, chat)
            if 'error' in response_data:
                return JsonResponse(response_data, status=500)
            else:
                return JsonResponse(response_data, safe=False)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def end_conversation(request):
    try:
        learner = request.user
        sri_lanka_tz = pytz.timezone('Asia/Colombo')

        # Find the active chat
        active_chat = Chat.objects.filter(learner=learner, chat_ended_at__isnull=True).last()
        if not active_chat:
            return JsonResponse({'error': 'No active chat found to end.'}, status=404)

        # Set the chat_ended_at time to now in Sri Lankan time
        active_chat.chat_ended_at = timezone.now().astimezone(sri_lanka_tz)
        active_chat.save()

        return JsonResponse({'success': 'Chat ended successfully.'})

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# Get chat history
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_chat_history(request):
    learner = request.user
    chats = Chat.objects.filter(learner=learner).order_by('-chat_started_at')
    serializer = ChatSerializer(chats, many=True)
    return JsonResponse(serializer.data, safe=False)

# Define the ChatHistoryView class if needed, based on your application's structure
