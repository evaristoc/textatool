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
import math
import scipy
import numpy



# def cleaningtext(norm_t, redo_corpus_by_sts, lensts, STOPWORDS):
#     st = []
#     countwds = len(norm_t)
#     for norm_w in norm_t:
#         if norm_w != '.':
#             if re.match(r'\w+', norm_w) and norm_w not in STOPWORDS:
#                 st.append(norm_w)
#         else:
#             redo_corpus_by_sts.append(st)
#             lensts.append(countwds)
#             st = []
#     if norm_w != '.':
#         redo_corpus_by_sts.append(st)
#         lensts.append(countwds)
#     return redo_corpus_by_sts, lensts

def cleaningtext(st, STOPWORDS = STOPWORDS):
    treated_st = []
    countwds = len(st)
    for w in st:
        if re.match(r'\w+', w) and w not in STOPWORDS:
            treated_st.append(w)
    return treated_st, countwds
            
def gensim_models(norm_posedsts, all_fd = {}, wordimportance = {}):
    NUM_TOPICS = 15
    STOPWORDS = nltk.corpus.stopwords.words('english') 
    redo_corpus_by_sts = []
    for norm_t in norm_posedsts:
        norm_sts = norm_t.split('.')
        for norm_st in norm_sts:
            redo_corpus_by_sts.append(cleaningtext(norm_st)[0])
    
    def basedonBOW(redo_corpus_by_sts):
        dictionary = gensim.corpora.Dictionary(redo_corpus_by_sts)
        corpus = [dictionary.doc2bow(text) for text in redo_corpus_by_sts]
    return corpus, dictionary
    
    def basedonTFIDF(corpus):
        return gensim.models.TfidfModel(corpus)
    
    def basedonOTHER(redo_corpus_by_sts, dictionary, wordimportance):
        def metriccalc1(w):
            return 1.0+2.0**float(wordimportance[w])
        
        corpus = []
        for sts in redo_corpus_by_sts:
            st = []
            for w in sts:
                st.append((dictionary.token2id[w], metriccalc1(w)))
            corpus.append(st)
        return corpus
        
    corpus, dictionary = basedonBOW(redo_corpus_by_sts)
    if wordimportance == {'tfidf':True}:
        tfidf = basedonTFIDF(corpus)
        corpus = tfidf[corpus]
    if wordimportance != {} and wordimportance != {'tfidf':True}:
        corpus = basedonOTHER(redo_corpus_by_sts, dictionary, wordimportance)
    
    
    lda_model = gensim.models.LdaModel(corpus=corpus, num_topics=NUM_TOPICS, id2word=dictionary)
    lsi_model = gensim.models.LsiModel(corpus=corpus, num_topics=NUM_TOPICS, id2word=dictionary)

   
    return lda_model, lsi_model


def raw_lda_frankjupyter(norm_posedsts, wordimportance):
    '''
    description: modified model based on https://www.frankcleary.com/svd/ for a more raw construction of a lda
    '''
    
    def metriccalc(st, normalizer, wordimportance):
        '''
        description:
        text normalization based on ALL characters in the sentence; why? Example: if two writers wrote 20 words, 2 of them very important, but one of them wrote half of characters stopwords, those 2 words wouldnt be penalized accordingly for this writer: the other wrote more important content
        '''       
        likedict = collections.defaultdict(float)
        textbow = collections.Counter(st)
        for w in st:
            #likedict[w] = math.pow(0.1+float(wordimportance[w]),textbow[w]/normalizer) #a sort of idf-normalization based on number of words in the text: the more the words in a text, the more important
            #likedict[w] = float(wordimportance[w])*textbow[w] #good but ignore those words with worimportance too low or 0 but that are frequent in text
            likedict[w] = 1.0+2.0**float(wordimportance[w]) #because it is not normilized this indicator would simply say that if it has the word at least once is already on topic
        return likedict
            
            
    STOPWORDS = nltk.corpus.stopwords.words('english')
    #redo_corpus_by_sts = []
    words_df = pandas.DataFrame()
    textreference = {}
    for textindex, norm_t in enumerate(norm_posedsts):
        print('norm_t', len(norm_t))
        redo_corpus_by_sts = []
        lensts = []
        norm_sts = norm_t.split('.')
        for stindex, norm_st in enumerate(norm_sts):
            treated_st, lensts = cleaningtext(norm_st)        
            print('treated_st', lensts)
            if len(treated_st) > 3:
                likedict = metriccalc(treated_st, lensts[stindex], wordimportance)
                st_df = pandas.DataFrame.from_dict(likedict, orient='index')
                textindexing = str(textindex)+'_'+str(stindex)
                st_df.columns = [textindexing]
                textreference[textindexing] = {}
                textreference[textindexing]['treated_st'] = treated_st
                #st_df.columns = [str(count)]
                words_df = words_df.join(st_df, how='outer', )
    
    words_df = words_df.fillna(0)
    print("Number of unique words: %s" % len(words_df))
    print(words_df.sort(columns=words_df.columns[0], ascending=False).head(10))
    
    return words_df, textreference


def dist(col1, col2, sigma):
    """Return the norm of (col1 - col2), where the differences in 
    each dimension are wighted by the values in sigma."""
    return numpy.linalg.norm(numpy.array(col1 - col2) * sigma)
    #return scipy.spatial.distance.cosine(col1,col2) #always saying they are different; also http://scikit-learn.org/stable/modules/generated/sklearn.metrics.pairwise.cosine_similarity.html


def similarityanalysis(words_df):
    
    U, sigma, V = numpy.linalg.svd(words_df)
    v_df = pandas.DataFrame(V, columns=words_df.columns)
    v_df.apply(lambda x: numpy.round(x, decimals=2))
     
    dist_df = pandas.DataFrame(index=v_df.columns, columns=v_df.columns)
    for cname in v_df.columns:
        dist_df[cname] = v_df.apply(lambda x: dist(v_df[cname].values, x.values, sigma))
    
    return dist_df, U, sigma, V, v_df
 
   
def dataviz(dist_df):

    #%matplotlib inline
    import matplotlib.pyplot as plt

    # plt.imshow(V, interpolation='none')
    # ax = plt.gca()
    # #plt.xticks(list(range(len(v_df.columns.values))))
    # #plt.yticks(list(range(len(v_df.index.values))))
    # plt.title("$V$")
    # #ax.set_xticklabels(v_df.columns.values, rotation=90)
    # plt.colorbar()
    # plt.show()
    
    
    # plt.imshow(dist_df.values, interpolation='none')
    # ax = plt.gca()
    # #plt.xticks(range(len(dist_df.columns.values)))
    # #plt.yticks(range(len(dist_df.index.values)))
    # #ax.set_xticklabels(dist_df.columns.values, rotation=90)
    # #ax.set_yticklabels(dist_df.index.values)
    # plt.title("Similarity between papers\nLower value = more similar")
    # print(dist_df.head())
    # plt.colorbar()
    # plt.show()

    #https://nlpforhackers.io/topic-modeling/
    #https://stackoverflow.com/questions/2455761/reordering-matrix-elements-to-reflect-column-and-row-clustering-in-naiive-python
    #https://stackoverflow.com/questions/7664826/how-to-get-flat-clustering-corresponding-to-color-clusters-in-the-dendrogram-cre/7668678
    #https://gmarti.gitlab.io/ml/2017/09/07/how-to-sort-distance-matrix.html
    #https://www.quora.com/How-do-you-combine-LDA-and-tf-idf vs https://stackoverflow.com/questions/44781047/necessary-to-apply-tf-idf-to-new-documents-in-gensim-lda-model
    #https://www.shanelynn.ie/select-pandas-dataframe-rows-and-columns-using-iloc-loc-and-ix/
    #https://docs.scipy.org/doc/scipy/reference/generated/scipy.cluster.hierarchy.dendrogram.html
    #https://joernhees.de/blog/2015/08/26/scipy-hierarchical-clustering-and-dendrogram-tutorial/
    #NO: https://www.programcreek.com/python/example/97741/scipy.cluster.hierarchy.dendrogram
    #https://stackoverflow.com/questions/11917779/how-to-plot-and-annotate-hierarchical-clustering-dendrograms-in-scipy-matplotlib
    #https://datawarrior.wordpress.com/tag/lda2vec/
    #https://stackoverflow.com/questions/47827130/suggestion-on-lda
    
    #heuristic text main idea extraction
    #http://bdewilde.github.io/blog/2014/09/23/intro-to-automatic-keyphrase-extraction/
    #https://pdfs.semanticscholar.org/dcd8/b259d530f16b66b9077903478306548df96a.pdf
    #https://books.google.nl/books?id=-e0ADQAAQBAJ&pg=PA104&lpg=PA104&dq=heuristic+text+main+idea+extraction&source=bl&ots=UefOlfKYHs&sig=Six23cBGcN4BU0AaFXSINYBsSWo&hl=nl&sa=X&ved=0ahUKEwj7i_aDo5fcAhVQDewKHemZBNAQ6AEIbzAJ#v=onepage&q=heuristic%20text%20main%20idea%20extraction&f=false
    #https://books.google.nl/books?id=-e0ADQAAQBAJ&printsec=frontcover&hl=nl#v=onepage&q&f=false
    #https://books.google.nl/books?id=lbQU3mP-9wMC&pg=PA254&lpg=PA254&dq=heuristic+text+main+idea+extraction&source=bl&ots=WQ_MCaf5Xe&sig=FGjG8ZqOAXeLevXJ5fx4TGPJWKU&hl=nl&sa=X&ved=0ahUKEwj7i_aDo5fcAhVQDewKHemZBNAQ6AEIYzAG#v=onepage&q=heuristic%20text%20main%20idea%20extraction&f=false
    #http://www.cs.columbia.edu/~gmw/candidacy/Fukumotoetal97.pdf
    #https://stackoverflow.com/questions/5025426/heuristic-approaches-to-finding-main-content
    #https://news.ycombinator.com/item?id=2344049
    
    import scipy.cluster.hierarchy as sch
    import pylab
    # Compute and plot dendrogram.
    fig = pylab.figure()
    axdendro = fig.add_axes([0.09,0.1,0.2,0.8])
    Y = sch.linkage(dist_df, method='centroid')
    Z = sch.dendrogram(Y, orientation='right')
    axdendro.set_xticks([])
    axdendro.set_yticks([])
    
    # Plot distance matrix.
    axmatrix = fig.add_axes([0.3,0.1,0.6,0.8])
    index = Z['leaves']
    print(index)
    dist_df = dist_df.iloc[index,:]
    dist_df = dist_df.iloc[:,index]
    im = axmatrix.matshow(dist_df, aspect='auto', origin='lower')
    axmatrix.set_xticks([])
    axmatrix.set_yticks([])
    
    # Plot colorbar.
    axcolor = fig.add_axes([0.91,0.1,0.02,0.8])
    pylab.colorbar(im, cax=axcolor)
    
    # Display and save figure.
    fig.show()
    #     
    # #redo_corpus_by_sts.append(st)
    
    

def showgensimmodelresults(model, NUM_TOPICS=10):
    for idx in range(NUM_TOPICS):
        # Print the first 10 most representative topics
        print("Topic #%s:" % idx, model.print_topic(idx, 20))
        print("=" * 20)



if __name__ == '__main__':

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
  
    lda_model, lsi_model = gensim_models(nor, fd, wordimportance)
    
    
    
    # words_df = raw_lda_frankjupyter(nor, wordimportance)
    # 
    # dist_df, U, sigma, V, v_df = similarityanalysis(words_df)
    # #showgensimmodelresults(lda_model)
    # #showgensimmodelresults(lsi_model) 
    #     
    # for paper in dist_df.columns:
    #     sim_papers_df = dist_df.sort(columns=paper)[paper]
    #     sim_papers = sim_papers_df.drop([paper]).index
    #     print('Papers most similar to ' + paper + ':')
    #     print(', '.join(sim_papers[:10]))
    #     print( '\n')
       
    #fn = processingData.jsonbuilding(al, nor, fd)
    
    #print(sorted(all_fd.items(), key=lambda x: x[1], reverse=True)[round(len(all_fd)/50):round(len(all_fd)/50)+10+1])
    
    #opacity, sizing, enlargedopacity = processingData.metrics_test(al, nor, fd)
    
