from django.http import JsonResponse
import pytz
import os
import PyPDF2
import openai
import numpy as np
import faiss
import json
from .models import Chat, ChatHistory
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.utils.timezone import now
from .serializers import ChatSerializer
from django.views import View
from django.conf import settings


# Set your OpenAI API key
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
embeddings = [get_embedding(chunk) for chunk in dataset_chunks]

# Convert embeddings to a numpy array
embeddings_np = np.array(embeddings).astype("float32")

# Create a FAISS index
index = None
if embeddings_np.shape[0] > 0 and embeddings_np.shape[1] > 0:
    index = faiss.IndexFlatL2(embeddings_np.shape[1])
    index.add(embeddings_np)
else:
    print("Error: embeddings_np has unexpected shape:", embeddings_np.shape)
    # Handle this case appropriately based on your application logic

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
        
        # # Define initial question and subsequent options based on user input
        # if current_focus is None:
        #     initial_question = "Which part of English is difficult for you? The options are: Grammar, Vocabulary, Writing."
        #     conversation_history.append({"role": "assistant", "content": initial_question})
        #     print("EduTech Assistant:", initial_question)
        #     current_focus = "initial"
        #     return initial_question
        
        # elif current_focus == "initial":
        #     if user_input.lower() in ["grammar", "vocabulary", "writing"]:
        #         current_focus = user_input.lower()
        #         if current_focus == "grammar":
        #             grammar_options = "In Grammar, what do you find difficult? The options are: Tenses, Parts of Speech, Sentence Structure, Punctuation."
        #             conversation_history.append({"role": "assistant", "content": grammar_options})
        #             print("EduTech Assistant:", grammar_options)
        #             return grammar_options
        #         elif current_focus == "vocabulary":
        #             vocabulary_options = "In Vocabulary, what do you find difficult? The options are: Word Meanings, Synonyms and Antonyms, Usage in Sentences."
        #             conversation_history.append({"role": "assistant", "content": vocabulary_options})
        #             print("EduTech Assistant:", vocabulary_options)
        #             return vocabulary_options
        #         elif current_focus == "writing":
        #             writing_options = "In Writing, what do you find difficult? The options are: Essay Writing, Letter Writing, Creative Writing."
        #             conversation_history.append({"role": "assistant", "content": writing_options})
        #             return writing_options
        #     else:
        #         invalid_option = "Please choose a valid option: Grammar, Vocabulary, Writing."
        #         conversation_history.append({"role": "assistant", "content": invalid_option})
        #         print("EduTech Assistant:", invalid_option)
        #         return invalid_option

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
        
        conversation_history = [
    {"role": "user", "content": "Can you help me understand passive voice?"},
    {"role": "assistant", "content": "Sure! Let's start with the basics. Here are some options: \n1. Definition of passive voice\n2. How to form the passive voice\n3. Examples of passive voice\nWhich one would you like to start with?"},
    {"role": "user", "content": "Definition of passive voice"},
    {"role": "assistant", "content": "Great choice! The passive voice is a type of sentence or clause in which the subject receives the action of the verb. For example, 'The book was read by the student.'\n\nCan you identify the subject and the verb in this sentence?"},
    # Assuming the student answers correctly
    {"role": "user", "content": "The book is the subject, and was read is the verb."},
    {"role": "assistant", "content": "That's correct! Now, let's move on to how to form the passive voice. Can you give me an example of an active voice sentence?"},
    # Assuming the student answers incorrectly
    {"role": "user", "content": "The cake was baked."},
    {"role": "assistant", "content": "Not quite. The sentence 'The cake was baked' is already in passive voice. An active voice sentence would be 'Someone baked the cake.' The subject 'someone' is performing the action of baking. Let's try again. Can you give me another example of an active voice sentence?"},
    # And so on...



    {"role": "user", "content": "Can you help me prepare for my English exam?"},
    {"role": "assistant", "content": "Of course! Which part of the exam would you like to start with?\n1. Comprehension passages\n2. Grammar\n3. Essay writing\n4. Letters\n5. Other parts"},
    {"role": "user", "content": "Let's start with comprehension passages."},
    {"role": "assistant", "content": "Sure! Here are some tips for approaching comprehension passages:\n- Skim the passage first\n- Read actively, underline key points\n- Answer questions strategically\n\nReady to practice with a passage, or would you like more tips?"},
    {"role": "user", "content": "I'd like more tips on grammar."},
    {"role": "assistant", "content": "Grammar is crucial! What specific grammar topic do you need help with?\n- Tenses\n- Pronouns\n- Sentence structure\n\nChoose one, or let me know if you have another topic in mind."},
    {"role": "user", "content": "Let's go with tenses."},
    {"role": "assistant", "content": "Perfect choice! Tenses are essential for expressing time in sentences. Would you like an overview of different tenses or examples of using them in sentences?"},
    {"role": "user", "content": "I'd like examples, please."},
    {"role": "assistant", "content": "Sure! Here's an example of present, past, and future tense:\n- Present: She writes novels.\n- Past: They visited Paris last summer.\n- Future: We will go to the beach tomorrow.\n\nDo you have any specific sentences you'd like to practice with, or shall we move on to another topic?"},
    {"role": "user", "content": "Let's move on to essay writing."},
    {"role": "assistant", "content": "Great! Essay writing involves structuring your ideas effectively. Do you need help with:\n- Introduction and thesis\n- Body paragraphs\n- Conclusion and summary\n\nChoose one, or if you have a specific question about essay writing, feel free to ask."},
    {"role": "user", "content": "I need help with structuring body paragraphs."},
    {"role": "assistant", "content": "Sure! Each body paragraph should focus on a single main idea or argument, supported by evidence or examples. Begin with a topic sentence, follow with supporting sentences, and conclude with a transition to the next paragraph.\n\nWould you like to outline a body paragraph together, or is there another part of the exam you want to cover?"},
    {"role": "user", "content": "I think I'm ready to practice writing a letter."},
    {"role": "assistant", "content": "Excellent! Letters are structured with:\n- Salutation\n- Introduction\n- Body (main message)\n- Conclusion\n- Closing\n\nDo you have a specific type of letter you need help with, or shall we go through the format together?"},
    {"role": "user", "content": "Let's go through the format together."},
    {"role": "assistant", "content": "Great! Let's start with the salutation. Depending on whether it's formal or informal, the salutation can vary. For example, 'Dear Mr. Smith' is formal, while 'Hi Sarah' is informal. What type of letter are you practicing for?"},
    {"role": "user", "content": "I'm practicing for a formal letter."},
    {"role": "assistant", "content": "Understood. In a formal letter, use 'Dear' followed by the recipient's title and last name, such as 'Dear Dr. Brown.' Let's continue with the introduction and the main body message. Do you have a scenario in mind for your letter, or shall we create one together?"}
]


        
        

        assistant_response = response['choices'][0]['message']['content'].strip()
        print("EduTech Assistant:", assistant_response)

        # Append assistant response to conversation history
        conversation_history.append({"role": "assistant", "content": assistant_response})
        
        ChatHistory.objects.create(
            chat = chat,
            message = user_input,
            response = assistant_response
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
            # Assume JSON payload {"user_input": "Your user input here"}
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
    
    #         if new_chat:
    #             active_chat = Chat.objects.filter(learner=learner, chat_ended_at__isnull=True).last()
    #             if active_chat:
    #                 active_chat.chat_ended_at = timezone.now().astimezone(pytz.timezone('Asia/Colombo'))
    #                 active_chat.save()
                    
    #             chat = Chat.objects.create(
    #                 learner = learner,
    #                 chat_title = user_input,
    #                 chat_started_at = timezone.now().astimezone(pytz.timezone('Asia/Colombo'))
    #             )
    #         else:
    #             chat_id = data.get('chat_id')
    #             if not chat_id:
    #                 chat = chat.objects.create(
    #                     learner = learner,
    #                     chat_title = user_input,
    #                     chat_started_at = timezone.now().astimezone(pytz.timezone('Asia/Colombo'))
    #                 )
    #             else:
    #                 chat = chat.objects.get(id=chat_id)
                    
    #         response_data = process_query(user_input, learner, chat)
    #         if 'error' in response_data:
    #             return JsonResponse(response_data, status=500)
    #         else:
    #             return JsonResponse(response_data, safe=False)
    #     except Exception as e:
    #         return JsonResponse({'error': str(e)}, status=500)
        
    # else:
    #     return JsonResponse({'error': 'Method not allowed'}, status=405)
                
    

# End conversation
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
# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def get_chat_history(request):
    # learner = request.user
    # chats = Chat.objects.filter(learner=learner).order_by('-chat_started_at')
    # serializer = ChatSerializer(chats, many=True)
    # return JsonResponse(serializer.data, safe=False)
  

# @permission_classes([IsAuthenticated])    
# class ChatHistoryView(View):
#     def get(self, request, *args, **kwargs):
#         learner = request.user  # Assuming you're using Django's authentication system
#         chats = Chat.objects.filter(learner=learner)

#         response_data = []
#         for chat in chats:
#             chat_data = {
#                 "chat_id": chat.chat_id,
#                 "learner": chat.learner_id,
#                 "chat_title": chat.chat_title,
#                 "chat_started_at": chat.chat_started_at.isoformat(),
#                 "chat_ended_at": chat.chat_ended_at.isoformat() if chat.chat_ended_at else None,
#                 "history": []
#             }

#             history = ChatHistory.objects.filter(chat=chat).order_by('timestamp')
#             for entry in history:
#                 chat_data["history"].append({
#                     "message": entry.message,
#                     "response": entry.response,
#                     "timestamp": entry.timestamp.isoformat()
#                 })

#             response_data.append(chat_data)

#         return JsonResponse(response_data, safe=False)
# views.py

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.http import JsonResponse
from .models import Chat, ChatHistory

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_chat_history(request):
    learner = request.user
    chats = Chat.objects.filter(learner=learner)

    response_data = []
    for chat in chats:
        chat_data = {
            "chat_id": chat.chat_id,
            "learner": chat.learner_id,
            "chat_title": "",  # Initialize an empty chat title
            "chat_started_at": chat.chat_started_at.isoformat(),
            "chat_ended_at": chat.chat_ended_at.isoformat() if chat.chat_ended_at else None,
            "history": []
        }

        # Get all messages for the current chat
        history = ChatHistory.objects.filter(chat=chat).order_by('timestamp')
        for entry in history:
            # Set the first message as chat title if it's not set yet
            # if not chat_data["chat_title"]:
            #     chat_data["chat_title"] = entry.message

            chat_data["history"].append({
                "message": entry.message,
                "response": entry.response,
                "timestamp": entry.timestamp.isoformat()
            })

        response_data.append(chat_data)
    
    return JsonResponse(response_data, safe=False)