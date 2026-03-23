import re
from collections import defaultdict
import string
from pathlib import Path
from nltk.stem import PorterStemmer
import sys

#Document Object
class Document:
    def __init__(self, doc_id: int, title: list[str], abstract: list[str], 
                 pub_date: str, authors: str):
        self.I = doc_id       # int
        self.T = title        # list of strings terms
        self.W = abstract     # list of strings terms
        self.B = pub_date     # string
        self.A = authors      # string

    def __repr__(self):
        return (f"Document(I={self.I}, "
                f"T={self.T}, "
                f"W={self.W}, "
                f"B='{self.B}', "
                f"A='{self.A}')")
    

#Gloabl Varibales
STOPWORD='Y'
STEMMING='N'
# Initialize stemmer
stemmer = PorterStemmer()
filename_stop="common_words"



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
def tokenize(text):
    result=[]
    for item in text:
        item= preprocess(item)
        if item != "":
            result+=item.lower().split()

    return result

#Load documents file
def load_documents_file(filename):
    #Reading the document
    with open(filename, 'r', encoding ="ascii", errors ="surrogateescape") as f:
        collection= f.read()
    f.close()

    return collection



#Load stopwords
def load_stopwords(filename):
    with open(filename, "r") as f:
        stopwords = set(f.read().lower().split())
    f.close
    return stopwords


def read_file(filename):
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

def remove_duplicates(terms):
    unique = []

    for term in terms:
        if term not in unique:
            unique.append(term)
    return unique



def createDictionary():
    
    stopwords=""
    #Geting the list of documents
    docs = read_file(filename_doc)
    dic_list={}
    for doc in docs:
        
        token=remove_duplicates(tokenize(doc.W))


        #Stop Applied
        stop_filtered=[]
        if STOPWORD == 'Y':
            #Loading stopwords
            stopwords= load_stopwords(filename_stop)
            for term in token:
                if term not in stopwords:
                    stop_filtered.append(term)
        else:
            for term in token:
                stop_filtered.append(term)

        #Stemming Applied
        stem_filtered=[]
        if STEMMING == 'Y':
            for term in stop_filtered:
                if term.isalpha():
                    stemmed = stemmer.stem(term)
                    stem_filtered.append(stemmed)
        else:
            for term in stop_filtered:
                if term.isalpha():
                    stem_filtered.append(term)


        for term in stem_filtered:
            if term not in dic_list:
                dic_list[term]=1
            else:
                dic_list[term]+=1
    

    
    #Sort the dictionary
    dic_key = list(dic_list.keys())
    dic_key.sort()

    sorted_dic = {i: dic_list[i] for i in dic_key}
    
    # Write to file
    with open("dictionary.txt", "w") as f:
        for term in sorted_dic:
            count = sorted_dic[term]
            f.write(f"{term},{count}\n")

    return sorted_dic, docs, stopwords


def createPostingList():
    # Get dictionary, documents, and stopwords
    dic, docs, stopwords = createDictionary()
    posting_list = defaultdict(list)

    for doc in docs:
        text = doc.W
        tokens = tokenize(text)
        replaced_text = []


        # Apply stopword filtering to replace stop words so you still count the position.
        if STOPWORD == 'Y':
            for term in tokens:
                if term in stopwords:
                   replaced_text.append("\\")
                else:
                    replaced_text.append(term)
        else:
            for term in tokens:
                replaced_text.append(term)

        # Track positions of each word
        word_positions = defaultdict(list)
        for pos, word in enumerate( replaced_text):
            
            if STEMMING == 'Y':
                stemmed_word = stemmer.stem(word)
                if stemmed_word in dic.keys():
                    word_positions[stemmed_word].append(pos+1)
            else:
                if word in dic.keys():
                    word_positions[word].append(pos+1)

        # Add to posting list
        for word, positions in word_positions.items():
            posting_list[word].append((doc.I, len(positions), positions))

    # Write posting list to file
    with open("posting_list.txt", "w") as f:
        for word in sorted(posting_list.keys()):
            f.write(f"{word}: {posting_list[word]}\n")
    

    return posting_list




    
createPostingList()
print("File created succesfully")
print("Exiting program.")
sys.exit()
