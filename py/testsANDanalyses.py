import sys, os

from dotenv import load_dotenv
load_dotenv(dotenv_path='../.env')
load_dotenv()

import pickle, json
import time
import processingData
import collections, itertools, copy, operator

import nltk
import pandas
import gensim
import sklearn
import re
import string

##################
## Previous data Preparation
#################

# with open(os.getcwd()+'/1_archive/data_foundjob.pkl', 'rb') as f_in:
#     data_saved = pickle.load(f_in)
# 
# for u in data_saved:
#     if data_saved[u]['forum']['foundjob_msg']['text'] != '':
#         print(data_saved[u]['forum']['foundjob_msg']['text'])
#         break
# 
# 
# for u in data_saved:
#     if data_saved[u]['forum']['foundjob_msg']['text'] != '':
#         soup_forum = BeautifulSoup(data_saved[u]['forum']['foundjob_msg']['text'])
#         break
with open('../data/jobproject_forum.json','r') as message:
    otp = json.load(message)
print(len(otp))
data = [{ "user": k, "data": otp[k] }  for k in otp]
print(len(data))
al, nor, fd = processingData.allrecordsLemmatization(processingData.allrecordsPreparation(data))
wordimportance = processingData.wordimportance_var2(nor,fd)

def weighted_lda(norm_posedsts, all_fd, wordimportance):
    NUM_TOPICS = 10
    STOPWORDS = nltk.corpus.stopwords.words('english')
    redo_corpus_by_sts = []
    for norm_t in norm_posedsts:
        st = []
        for norm_w in norm_t:
            if norm_w in STOPWORDS:
                continue
            if norm_w != '.':
                if re.match(r'\w+', norm_w):
                    st.append(norm_w)
            else:
                redo_corpus_by_sts.append(st)
        if norm_w != '.':
            redo_corpus_by_sts.append(st)
    dictionary = gensim.corpora.Dictionary(redo_corpus_by_sts)
    corpus = [dictionary.doc2bow(text) for text in redo_corpus_by_sts]
    
    print(len(redo_corpus_by_sts))
    
    lda_model = gensim.models.LdaModel(corpus=corpus, num_topics=NUM_TOPICS, id2word=dictionary)
    lsi_model = gensim.models.LsiModel(corpus=corpus, num_topics=NUM_TOPICS, id2word=dictionary)

   
    return lda_model, lsi_model

def showmodelresults(model, NUM_TOPICS=10):
    for idx in range(NUM_TOPICS):
        # Print the first 10 most representative topics
        print("Topic #%s:" % idx, model.print_topic(idx, 20))
        print("=" * 20)

lda_model, lsi_model = weighted_lda(nor, fd, wordimportance)

showmodelresults(lda_model)
showmodelresults(lsi_model)
            
    
    
#fn = processingData.jsonbuilding(al, nor, fd)

#print(sorted(all_fd.items(), key=lambda x: x[1], reverse=True)[round(len(all_fd)/50):round(len(all_fd)/50)+10+1])

#opacity, sizing, enlargedopacity = processingData.metrics_test(al, nor, fd)