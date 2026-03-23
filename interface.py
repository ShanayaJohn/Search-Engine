import sys
from pathlib import Path
import time
from search import read_file, load_posting_list, load_dictionary, load_stopwords, search_post
import math


print("Welcome to Inverted Index Central.\nBefore we begin, please answer the following so I can better tailor your experience.\n")

print("Please include the path of main list of documents:\nTo exit type: zzend")
filename_doc = input().strip()

while True:
    if filename_doc.lower() == "zzend":
        print("Exiting program.")
        sys.exit()

    if Path(filename_doc).exists():
        break
    else:
        print("File not found. Please enter a valid path.")
        filename_doc = input("Please include the path of main list of documents:\nTo exit type: zzend\n").strip()


print()

print("Please include the path to the dictionary:\nTo exit type: zzend.")
filename_dic = input().strip()
while True:
    if filename_dic.lower() == "zzend":
        print("Exiting program.")
        sys.exit()

    if Path(filename_dic).exists():
        break
    else:
        print("File not found. Please enter a valid path.")
        filename_dic = input("Please include the path to the dictionary:\nTo exit type: zzend\n").strip()

print()

print("Please include the path to the Posting List Document:\nTo exit type: zzend.")
filename_post = input().strip()
while True:
    if filename_post.lower() == "zzend":
        print("Exiting program.")
        sys.exit()

    if Path(filename_post).exists():
        break
    else:
        print("File not found. Please enter a valid path.")
        filename_post = input("Please include the path to the Posting List Document:\nTo exit type: zzend.\n").strip()

print()





# Store Query start and end times
query_times = [] 


#Loading all the documents
documents=read_file(filename_doc)
posting_list=load_posting_list(filename_post)
dictionary=load_dictionary(filename_dic)
stopwords = load_stopwords("common_words") 

#Calculate the idf for the entire dictionary
N = len(documents)
idf = {term: math.log(N / df, 10) if df > 0 else 0 for term, df in dictionary.items()}

doc_map = {doc.I: doc for doc in documents}

print("Enter a term:\nTo exit type: zzend")
TERM = ""

while TERM != "zzend":
    TERM = input().lower()

    if TERM != "zzend":
        start_time = time.time()  

        rank_doc = search_post(TERM, documents, posting_list, dictionary, stopwords, idf,doc_map)

       
        print("\nRelevant Documents:")
       
        for doc_id, score in rank_doc.items():
            doc = doc_map.get(doc_id)
            title = " ".join(doc.T).strip()
            author = doc.A.strip() if doc.A and doc.A.strip() else None
            print(f"Document ID: {doc_id}")
            print(f"Title: {title}" + (f" by {author}" if author else ""))
            print(f"Score: {round(score, 4)}")
            print()   
        end_time = time.time()   
        duration = end_time - start_time

        query_times.append(duration) 
        print("Query time:", round(duration, 4), "seconds\n")
        print("Enter a term: \nTo exit type: zzend")

# Calculate average
if len(query_times) > 0:
    total_time = 0
    for t in query_times:
        total_time += t

    average_time = total_time / len(query_times)
    print("\nAverage query time:", round(average_time, 4), "seconds")
else:
    print("\nNo valid queries were entered.")