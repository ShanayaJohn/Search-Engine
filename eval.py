from search import read_file, load_posting_list, load_dictionary, load_stopwords, search_post, load_documents_file
import math
import time
import re



def parse_queries(filename="query.text"):
    queries = {}
    doc_queries = load_documents_file(filename)  # Use the filename parameter
    list_of_queries = doc_queries.split(".I ")[1:]  # Skip the first empty split

    for query in list_of_queries:
        parts = re.split(r'(?m)^(\.[A-Z])', query)

    
        qid = int(parts[0].strip())  # Strip whitespace before converting to int
        
        for i in range(1, len(parts), 2):
            key = parts[i]
            value = parts[i + 1].strip()
            if key == ".W":
                queries[qid] =value.replace("\n", " ")
                break  

    return queries

def parse_qrels(filename="qrels.text"):
    qrels = {}
    doc_qrels = load_documents_file(filename).splitlines()

    for line in doc_qrels:
        parts = line.strip().split()
        num = int(parts[0])
        doc = int(parts[1])

        if num in qrels:
            qrels[num].append(doc)
        else:
            qrels[num] = [doc]

    return qrels


def process_term():
    #Loading all the documents
    documents=read_file()
    posting_list=load_posting_list()
    dictionary=load_dictionary()

    #Calculate the idf
    N = len(documents)
    idf = {term: math.log(N / df, 10) if df > 0 else 0 for term, df in dictionary.items()}
    
    doc_map = {doc.I: doc for doc in documents}

    
    stopwords = load_stopwords()
    queries = parse_queries()
    qrel = parse_qrels()
    AP = []
    P_R = []

    for qid, query in queries.items():
        result = list(search_post(query, documents, posting_list, dictionary, stopwords, idf,doc_map).keys())
        relevant_docs = qrel.get(qid, [])

        # Calculate precision at each relevant doc
        precision_values = []
        retrieved_relevant = 0

        for i, doc_id in enumerate(result):
            if doc_id in relevant_docs:
                retrieved_relevant += 1
                precision = retrieved_relevant / (i + 1)
                precision_values.append(precision)

        # Average Precision (AP)
        ap = sum(precision_values) / len(relevant_docs) if relevant_docs else 0
        AP.append(ap)

        # R-Precision: precision at rank R = number of relevant docs
        R = len(relevant_docs)
        top_R = result[:R]
        r_relevant = sum(1 for doc_id in top_R if doc_id in relevant_docs)
        r_precision = r_relevant / R if R > 0 else 0
        P_R.append(r_precision)

    # Final metrics
    MAP = sum(AP) / len(AP) if AP else 0
    avg_r_precision = sum(P_R) / len(P_R) if P_R else 0

    print(f"Mean Average Precision (MAP): {MAP:.4f}")
    print(f"Average R-Precision: {avg_r_precision:.4f}")

start_time = time.time()

# Your code here
process_term()

end_time = time.time()
elapsed = end_time - start_time

print(f"Execution time: {elapsed:.4f} seconds")