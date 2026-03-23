import re
import string
from nltk.stem import PorterStemmer
import ast
import math

class Document:
    def __init__(self, doc_id: int, title: str, abstract: list[str], 
                 pub_date: str, authors: str):
        self.I = doc_id       
        self.T = title        
        self.W = abstract     
        self.B = pub_date     
        self.A = authors      

    def __repr__(self):
        return (f"Document(I={self.I}, "
                f"T={self.T}, "
                f"W={self.W}, "
                f"B='{self.B}', "
                f"A='{self.A}')")
    
    

#Global Varibales
STOPWORD='Y'
STEMMING='N'
# Initialize stemmer
stemmer = PorterStemmer()


#Takes input string and removes punctions, numbers, brackets, special characters
def preprocess(text):

    # Remove punctuation
    text = text.translate(str.maketrans('', '', string.punctuation))
    #lowercase
    text = text.lower().strip()

    # Remove tabs and newline characters
    text = re.sub(r'[\t\n\r]', ' ', text)
    return text

#Takes input list for string sentence and returns a string of terms
def tokenize(text,FLAG):
    result=[]
    for item in text:
        if FLAG:
            item= preprocess(item).lower()
        if item != "":
            result+=item.split()

    return result

#Load dictionary document
def load_dictionary(filename="dictionary.txt"):
    dic = {}
    with open(filename, "r") as f:
        for line in f:
            word, count = line.strip().split(",")
            dic[word] = int(count)
    f.close()
    return dic

#Load Posting List document
def load_posting_list(filename="posting_list.txt"):
    posting_list = {}

    with open(filename, "r") as f:
        for line in f:
            if ":" in line:
                term, postings_items = line.strip().split(":", 1)
                postings = ast.literal_eval(postings_items.strip()) # Turn my string into list of tuples
                posting_list[term] = postings
    f.close()
    return posting_list

#Load documents file
def load_documents_file(filename):
    #Reading the document
    with open(filename, 'r', encoding ="ascii", errors ="surrogateescape") as f:
        collection= f.read()
    f.close()

    return collection

#Load stopwords
def load_stopwords(Filename="common_words"):
    with open(Filename, "r") as f:
        stopwords = set(f.read().lower().split())
    f.close
    return stopwords

#Read the collection and creates document objects
def read_file(filename="cacm.all"):
    documents = []

    #Reading the document
    collection=load_documents_file(filename)

    #Separating the documents
    list_of_documents = collection.split(".I ")[1:]

   
    for doc in list_of_documents:
        fields_to_keep = { '.T', '.W', '.B', '.A'}
        # Split by any ".<char>" line
        parts = re.split(r'(?m)^(\.[A-Z])', doc)
        

        # Build dictionary with only desired fields
        doc_dict = {}
        for i in range(1, len(parts), 2):
            key = parts[i]
            value = parts[i+1].strip()
            if key in fields_to_keep:
                doc_dict[key] = value

        # Extract each field safely
        doc_id = int(parts[0].lstrip())
        title = doc_dict.get('.T', "").split("\n")
        abstract = doc_dict.get('.W', "").split("\n") if '.W' in doc_dict else []
        pub_date = doc_dict.get('.B', "")
        authors = doc_dict.get('.A', "")

        title=title
        abstract=title+ abstract
        doc = Document(doc_id=doc_id, title=title, abstract=abstract, 
                       pub_date=pub_date, authors=authors)
        documents.append(doc)

    return documents

#Calculations the cosine similarity 
def search_post(term, documents, posting_list, dictionary, stopwords,idf, doc_map):

    # Preprocess query
    query_tokens = tokenize([term], True)
    if STOPWORD == 'Y':
        query_tokens = [t for t in query_tokens if t not in stopwords]
    if STEMMING == 'Y':
        query_tokens = [stemmer.stem(t) for t in query_tokens if t.isalpha()]
    else:
        query_tokens = [t for t in query_tokens if t.isalpha()]

    # Find documents that contain the query terms
    doc_ids = set()
    for t in query_tokens:
        postings = posting_list.get(t, [])
        for docid, _, _ in postings:
            doc_ids.add(docid)

      

    # Extract all terms from relevant documents
    all_terms = []
    for doc_id in doc_ids:
        doc = doc_map[doc_id]
        tokens = tokenize(doc.W, True)
        tokens = [t for t in tokens if t in dictionary]
        all_terms += tokens

    # Remove duplicates and sort alphabetically
    terms = sorted(set(all_terms))

     #Create dictionary that store all term frequency of each document
    posting_lookup = {}
    for term, postings in posting_list.items():
        if term in terms:
            term_postings = {} 
            for post in postings:
                docid = post[0]  
                f =post[1]   # Term frequency
                term_postings[docid] = f
            posting_lookup[term] = term_postings



    # Build document vectors
    doc_vectors = {}
    for doc_id in doc_ids:
        vec = []
        for term in terms:
            freq = posting_lookup.get(term, {}).get(doc_id, 0)
            if freq > 0:
                tf= math.log(freq, 10) + 1
                w = tf * idf[term]
                vec.append(w)
            else:
                vec.append(0)
        doc_vectors[doc_id] = vec

    # Build query vector
    query_vector = []
    query_term_counts = {t: query_tokens.count(t) for t in terms if t in query_tokens}
    for term in terms:
        if term in query_term_counts:
            tf = math.log(query_term_counts[term], 10) + 1
            w = tf * idf[term]
            query_vector.append(w)
        else:
            query_vector.append(0)

    # Calcualte the distance
    doc_dist = {}
    for doc_id, vec in doc_vectors.items():
        total = sum(w**2 for w in vec)
        dis = math.sqrt(total)
        doc_dist[doc_id] = dis

    #Distance for the query
    query_dist = math.sqrt(sum(w**2 for w in query_vector))
   
    #Normalize the document vector using the distance
    for doc_id, vec in doc_vectors.items():
        norm = doc_dist.get(doc_id)
        doc_vectors[doc_id] = [w / norm for w in vec] # normalize each value in the vector

    #Normalize the query vector
    if query_dist > 0:
        query_vector = [w / query_dist for w in query_vector]

    
    # Cosine similarity
    sim = {}
    for doc_id, vector in doc_vectors.items():
        dot_product = sum(w1 * w2 for w1, w2 in zip(query_vector, vector))
        sim[doc_id] = dot_product

    #Sort the si
    ranked_sim = sorted(sim.items(), key=lambda x: x[1], reverse=True)
    
    
    result = {}
    for doc_id, score in ranked_sim:
        if score > 0:
            result[doc_id] = score

    return result
