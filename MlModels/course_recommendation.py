import numpy  as np
import pandas as pd
from rake_nltk import Rake
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer
import re


def load_data():
    dataset = pd.read_csv("dataset/course_list.csv")
    print(dataset)
    return dataset

# def getKeywords(sentence):
#     Keywords = []
#     r = Rake()
#     r.extract_keywords_from_text(sentence)
#     Keywords.append(list(r.get_word_degrees()))
#     return Keywords

# def Bag_Of_Words(ds):
#     course_kw = getKeywords(ds,'course_title')
#     subject_kw = getKeywords(ds,'subject')
#     bag= []
#     for i,j in zip(course_kw,subject_kw):
#         bag.append(i+j)
#     BoW = []
#     for i in bag:  
#         BoW.append(" ".join(i))
#     return BoW

# def cosinevectors():
#     count = CountVectorizer()
#     count_matrix = count.fit_transform(Bag_Of_Words)
#     cosine_sim = cosine_similarity(count_matrix, count_matrix)
#     dataset['Words_Vector'] = ""
#     dataset['Words_Vector'] = cosine_sim
  
  
def recommendindex(dataset,kw):
    coursename = kw
    r = Rake()
    r.extract_keywords_from_text(coursename)
    cname = " ".join(r.get_word_degrees())
    recom_course_index = dataset[dataset['Bag_Of_Words'].str.contains(
        cname,regex=True
        )].sort_values('Words_Vector',ascending = False)[0:10].index
    return recom_course_index

def recommend(val):
    dataset = load_data()
    res = recommendindex(dataset,val)
    listofindex = []
    for i in res:
        listofindex.append(str(i))
    indexs = ",".join(listofindex)
    return indexs
    

    
    

