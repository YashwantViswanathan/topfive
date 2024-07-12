from django.shortcuts import render

# Create your views here.

from django.shortcuts import render
from django.http import HttpResponse
from .forms import SimilarityForm
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# Path to the Excel file
file_path = '/Users/viswanathan/Downloads/VisteonItem.xlsx'

# Read the Excel file into a DataFrame
try:
    df = pd.read_excel(file_path, engine='openpyxl')
except Exception as e:
    print(f"Error reading Excel file: {e}")
    raise

# Check if 'PartDescription' column exists (case-insensitive)
part_description_col = None
for col in df.columns:
    if col.strip().lower() == 'partdescription':
        part_description_col = col
        break

if part_description_col is None:
    raise KeyError("The 'PartDescription' column does not exist in the Excel file.")

# Extract the 'PartDescription' column and convert it to a list
sentences_list = df[part_description_col].dropna().tolist()

def find_top_five_similar(input_sentence, sentences_list):
    documents = [input_sentence] + sentences_list
    tfidf_vectorizer = TfidfVectorizer()
    sparse_matrix = tfidf_vectorizer.fit_transform(documents)
    similarity_matrix = cosine_similarity(sparse_matrix)
    similarity_scores = similarity_matrix[0, 1:]
    df_sim = pd.DataFrame({'sentence': sentences_list, 'similarity_score': similarity_scores})
    df_sim = df_sim.sort_values(by='similarity_score', ascending=False)
    top_five = df_sim.head(5)
    return top_five

def process_chunks(input_sentence, sentences_list, chunk_size=10000):
    num_chunks = int(np.ceil(len(sentences_list) / chunk_size))
    overall_top_five = pd.DataFrame(columns=['sentence', 'similarity_score'])
    for i in range(num_chunks):
        start_idx = i * chunk_size
        end_idx = min((i + 1) * chunk_size, len(sentences_list))
        chunk = sentences_list[start_idx:end_idx]
        top_five_similar = find_top_five_similar(input_sentence, chunk)
        overall_top_five = pd.concat([overall_top_five, top_five_similar])
    overall_top_five = overall_top_five.sort_values(by='similarity_score', ascending=False).head(5)
    return overall_top_five

def similarity_view(request):
    if request.method == 'POST':
        form = SimilarityForm(request.POST)
        if form.is_valid():
            input_sentence = form.cleaned_data['input_sentence']
            top_five_similar = process_chunks(input_sentence, sentences_list)
            return render(request, 'similarity/result.html', {'form': form, 'top_five_similar': top_five_similar})
    else:
        form = SimilarityForm()
    return render(request, 'similarity/similarity.html', {'form': form})



from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

# Make sure your previous imports are still there
# from django.shortcuts import render
# from django.http import HttpResponse
# from .forms import SimilarityForm
# import pandas as pd
# from sklearn.feature_extraction.text import TfidfVectorizer
# from sklearn.metrics.pairwise import cosine_similarity
# import numpy as np

@csrf_exempt
def similarity_api_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            input_sentence = data.get('input_sentence', '')

            # Process the input_sentence to find top five similar sentences
            top_five_similar = process_chunks(input_sentence, sentences_list)

            # Convert the results to a list of dictionaries
            results = top_five_similar.to_dict('records')
            return JsonResponse({'status': 'success', 'data': results}, status=200)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    else:
        return JsonResponse({'status': 'error', 'message': 'Only POST requests are allowed'}, status=405)
