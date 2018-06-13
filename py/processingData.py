import os
import re
import nltk
import json
print("in the other",os.getenv("TEST_MULTILINE_VAR"))
nltk.data.path.append(os.getenv("NLTKDATADIR"))
from nltk.corpus import stopwords
from bs4 import BeautifulSoup
import copy
import math


def allrecordsPreparation(allrecords):
	'''
	description: tokenization and POS tagging
	input: dict of allrecords texts and data from different sources
	treatment: separating only those with posts in the forum and tokenizing the posts
	output:
	1) list of lists, each with:
	-- id
	-- username
	-- link of the post
	-- tokenized text
	-- POS tagged text
	2) list of post ids
	'''
	print('in allrecordsPreparation (len(allrecords))::',len(allrecords))
	#global var to this scope
	#forum_tonltk = []
	tktexts = []
	soup_forum = None
	forum_ids = []
	all_posedsts = []
	count = 0
	for u in allrecords:
		#block arguments
		record = u["data"]
		forumpost = record['forum']['foundjob_msg']['text']
		if forumpost == '':
			continue
		forumpostID = record['forum']['foundjob_msg']['id']
		forumpostLINK = record['forum']['foundjob_msg']['link']
		soup_forumpost = BeautifulSoup(forumpost)
		soup_forumpostTEXT = soup_forumpost.find('body').get_text()
		tksoup_forumpostTEXT = nltk.word_tokenize(soup_forumpostTEXT)
		
		#forum_tonltk.append(soup_forumpostTEXT)
		
		#listoftexts_forum.append(('f_'+forumpostID,
		#                          [w.lower() for w in tksoup_forumpostTEXT],
		#                          forumpostLINK,
		#                          u))
		
		modtext = []
		for w in tksoup_forumpostTEXT:
			w = w.lower()
			rws = []
			if len(w) > 1 and len({'.','-',':'}.intersection(w)) >= 1:
				#print(w)
				for punc in {'.','-',':'}.intersection(w):
					rws = w.replace(punc, ' '+punc+' ').split()
				#print(rws)
			if len(rws) == 0:
				modtext.append(w)
			else:
				for w in rws:
					modtext.append(w)
			
		#[w.lower() for w in nltk.word_tokenize(soup_forum.find('body').get_text())]
		all_posedsts.append((
							'f_'+forumpostID,
							u["user"],
							forumpostLINK,
							modtext,
							nltk.pos_tag(modtext)
							))
		#forum_ids.append(forumpostID)
	
		count += 1

	print("number of treated posts (len(count)) ::", count)
	#return all_posedsts, forum_ids
	return all_posedsts

def allrecordsLemmatization(all_posedsts):
    '''
    description: lematization
    input: list of tokenized texts (sentences)
    output:
        1) same list of texts but each with the lematized words when found
        2) freqDist of the words after trying lematization
    '''
    norm_posedsts = []
    allnorm_posedwords = []

    print("-"*15+"\nFails to lematize will be printed below\n"+"-"*15)
    for posedpost in all_posedsts:
        norm_posedws = []
        merged_posedsts = posedpost[4]
                
        for posw in  merged_posedsts:
            w = posw[0]
            pos = posw[1]
            if nltk.corpus.wordnet.synsets(w):
                try:
                    n = ''
                    if nltk.corpus.wordnet.synsets(w,pos[0].lower())[0].root_hypernyms()[0].name().split('.')[0] == 'entity':
                        n = w
                    else:
                        n = nltk.corpus.wordnet.synsets(w,pos[0].lower())[0].root_hypernyms()[0].name().split('.')[0]
                    if pos[0] == 'V':
                        n = nltk.stem.wordnet.WordNetLemmatizer().lemmatize(w,'v')
                    if pos == 'NNS' or pos == 'NN$':
                        n = nltk.stem.wordnet.WordNetLemmatizer().lemmatize(w)
                    #print(w, nltk.corpus.wordnet.synsets(w,pos[0].lower())[0].root_hypernyms(), n)
                    norm_posedws.append(n)
                    allnorm_posedwords.append(n)
                except KeyError: #in some cases the POS tag is not recognised by wordnet synset
                    print("pos KeyErrors", w,pos)
                    norm_posedws.append(w)
                    allnorm_posedwords.append(w)
                except IndexError:
                    print("IndexErrors (not found)", w,pos) #in some cases (w,pos) pair was not found at some point of the synsets root hyernyms
                    #print(nltk.corpus.wordnet.synsets(w,pos[0].lower()))
                    norm_posedws.append(w)
                    allnorm_posedwords.append(w)                    
            else:
                #print(w, [])
                norm_posedws.append(w)
                allnorm_posedwords.append(w)
        
        norm_posedsts.append(norm_posedws)
    
    all_fd = nltk.FreqDist(allnorm_posedwords)
    
    return all_posedsts, norm_posedsts, all_fd

# def normalization(norm_posedsts):
# 
#     #idf based on https://stevenloria.com/tf-idf/
#     def n_containing(word, bloblist):
#         return sum(1 for blob in bloblist)
# 
#     def idf(word, bloblist):
#         return math.log(len(bloblist) / (1 + n_containing(word, bloblist)))
# 
#     merged_posedsts = list(itertools.chain(*[posedst for posedst in norm_posedsts])) #expand the several nested lists in the norm_posedsts list
# 
#     all_fd = nltk.FreqDist(merged_posedsts) #the expansion is just the words
#     
#     return all_fd

# def htmlpagebuilding(all_posedsts, norm_posedsts, all_fd):
#     '''
#     description: creating an html of a lemmatized text highlighting lemmatized words that are LESS common to corpora
#     input:
#         1) tokenized list of texts
#         2) same list as above but with lemmatized words
#         3) freqDist of lemmatized words
#     output: html template; highlighting based on opacity
#     '''
#     html_test = ''
#     maxdiv = math.log(sorted(all_fd.items(), key=lambda x: x[1], reverse=True)[0][1])
# 
#     for i,norm_t in enumerate(norm_posedsts):
#         
#         if all_posedsts[i][1] != 'gcamacho079':
#             continue
#         else:
#         
#             doc_df = nltk.FreqDist(t)
#             
#             html_test=html_test+'<h3> TEXT '+str(i)+'</h3><p><a href='+all_posedsts[i][2][:-5]+'>link</a> by '+all_posedsts[i][1]+'</p><p>'
#             for w in norm_t:
#                 opacity_based_on_tfish = str(1-math.log(all_fd[w])/maxdiv)[:3]
#                 size_based_on_tfish = str((1-all_fd[w]/maxdiv)*20)[:3]
#                 html_test=html_test+"<span style='opacity:"+opacity_based_on_tfish+";'>"+w+" </span>"
#                 if w == '.':
#                     html_test=html_test+'</p><p>'
#             html_test=html_test+'<br>'
#             return html_test



def jsonbuilding(all_posedsts, norm_posedsts, all_fd):
    '''
    description: creating a lemmatized text with highlighting lemmatized words that are LESS common to corpora; formula to highlight is 1 - log(frqDist_wd)/log(frqDist_mostcommonwd) --- the most common word as reference
    input:
        1) tokenized list of texts
        2) same list as above but with lemmatized words
        3) freqDist of lemmatized words
    output: html template; highlighting based on opacity
    '''

    maxdiv = math.log(sorted(all_fd.items(), key=lambda x: x[1], reverse=True)[0][1])
    data_out = []
    l = 0
    for i,norm_t in enumerate(norm_posedsts):
        tkpost = all_posedsts[i][3]
        rcd = {'id': all_posedsts[i][0], 'author': all_posedsts[i][1], 'link': all_posedsts[i][2][:-5],'wPERst':[]}    
        #doc_df = nltk.FreqDist(norm_t)
        st = {'st_index': l, 'tokens':[]}
        for k, norm_w in enumerate(norm_t):
            thisword = math.log(all_fd[norm_w])
            opacity_based_on_tfish = str(1-thisword/maxdiv)[:3]
            #size_based_on_tfish = str((1-all_fd[norm_w]/maxdiv)*20)[:3]
            st['tokens'].append({'token':tkpost[k], 'ltoken':norm_w, 'val':opacity_based_on_tfish})
            if norm_w == '.':
                st['tokens'].append({'token':tkpost[k], 'ltoken':norm_w, 'val':opacity_based_on_tfish})
                stc = copy.deepcopy(st)
                rcd['wPERst'].append(stc)
                l += 1
                st = {'st_index': l, 'tokens':[]}
        l = 0
        st = {'st_index': l, 'tokens':[]}
        data_out.append(copy.deepcopy(rcd))
        
        
    return data_out



def metrics_test(all_posedsts, norm_posedsts, all_fd):
    '''
    description: OJO: no normalization applied to the metrics
    input:
        1) tokenized list of texts
        2) same list as above but with lemmatized words
        3) freqDist of lemmatized words
    output: 
    '''

    maxdiv = math.log(sorted(all_fd.items(), key=lambda x: x[1], reverse=True)[0][1])
    opacity = dict([(k, 1-math.log(v)/maxdiv) for k,v in all_fd.items()])
    sizing_matrix = dict([(k, [0]*len(all_posedsts)) for k in list(all_fd.keys())])
    data_out = []
    l = 0
    for i,norm_t in enumerate(norm_posedsts):
        tkpost = all_posedsts[i][3]
        rcd = {'id': all_posedsts[i][0], 'author': all_posedsts[i][1], 'link': all_posedsts[i][2][:-5],'wPERst':[]}    
        #doc_df = nltk.FreqDist(norm_t)
        # st = {'st_index': l, 'tokens':[]}
        for k, norm_w in enumerate(norm_t):
        #    opacity_based_on_tfish = str(opacity[norm_w])[:3]
            sizing_matrix[norm_w][i] = sizing_matrix[norm_w][i] + 1
        #     st['tokens'].append({'token':tkpost[k], 'ltoken':norm_w, 'val':opacity_based_on_tfish})
        #     if norm_w == '.':
        #         st['tokens'].append({'token':tkpost[k], 'ltoken':norm_w, 'val':opacity_based_on_tfish})
        #         stc = copy.deepcopy(st)
        #         rcd['wPERst'].append(stc)
        #         l += 1
        #         st = {'st_index': l, 'tokens':[]}
        # l = 0
        # st = {'st_index': l, 'tokens':[]}
        data_out.append(copy.deepcopy(rcd))
        
    sizing = dict([(k, 1 - max(vector)/sum(vector)) for k, vector in sizing_matrix.items()])
    
    enlargedopacity = dict([(k, valsizing*opacity[k]) for k, valsizing in sizing.items()])
        
    #return data_out
    return opacity, sizing, enlargedopacity


def enlargedopacity(norm_posedsts, all_fd):
    '''
    description: "enlargedopacity" is just a metric to measure word importance; the importance of a word in this case is based
    on the combined effect of two metrics:
    --- opacity: 1 - total count of word against total count of the most frequent word (1 - log(f_w)/log(f_maxw)):
        this range between [0,1); the metric will penalize those words that are too frequent in the corpus, giving it a small value (close to 0)
    --- sizing: 1 - (max count of a word in a text) / (total count of the word in all texts):
        this range between [0,1); this metric is mostly a dispersion metric: the smaller the value, the larger the likelihood
        that the word concentrates in only one text; it also penalises a very rare words
    
    enlargedopacity is the product of the frequency of the word against the most frequent word by its dispersion in the corpus
    
    While opacity will favour the less frequent words, sizing will adjust opacity so those that are too concentrated in very few texts (too rare) get penalized.
    Using sizing as dispersion metric, words that are more common between different text receive better ranking.
    
    The idea is to highlight those words that are more shared in the corpus without being too frequent ones. Those are more like (shared) topic words.
    
    Be aware that the metric is not normalized by text's length: the effect of the frequent appearance of a word because the text is long is not considered
    This could affect mostly the dispersion metric.
    
    input:
        1) tokenized list of texts
        2) freqDist of lemmatized words
    
    output: enlargedopacity 
    '''

    maxdiv = math.log(sorted(all_fd.items(), key=lambda x: x[1], reverse=True)[0][1])
    opacity = dict([(k, 1-math.log(v)/maxdiv) for k,v in all_fd.items()])
    sizing_matrix = dict([(k, [0]*len(norm_posedsts)) for k in list(all_fd.keys())])
    data_out = []
    l = 0
    for i,norm_t in enumerate(norm_posedsts):
        for k, norm_w in enumerate(norm_t):
            sizing_matrix[norm_w][i] = sizing_matrix[norm_w][i] + 1
       
    sizing = dict([(k, 1 - max(vector)/sum(vector)) for k, vector in sizing_matrix.items()])
    
    enlargedopacity = dict([(k, valsizing*opacity[k]) for k, valsizing in sizing.items()])

    return enlargedopacity



def jsonbuildingnew(all_posedsts, norm_posedsts, metrics):
    '''
    description: creating a lemmatized text with highlighting lemmatized words that are LESS common to corpora; formula to highlight is 1 - log(frqDist_wd)/log(frqDist_mostcommonwd) --- the most common word as reference
    input:
        1) tokenized list of texts
        2) same list as above but with lemmatized words
        3) a metric used to mark the words in html
    output: html template; highlighting based on opacity
    '''

    data_out = []
    l = 0
    for i,norm_t in enumerate(norm_posedsts):
        tkpost = all_posedsts[i][3]
        rcd = {'id': all_posedsts[i][0], 'author': all_posedsts[i][1], 'link': all_posedsts[i][2][:-5],'wPERst':[]}    
        st = {'st_index': l, 'tokens':[]}
        for k, norm_w in enumerate(norm_t):
            opacity_based_on_tfish = str(metrics[norm_w])[:3]
            st['tokens'].append({'token':tkpost[k], 'ltoken':norm_w, 'val':opacity_based_on_tfish})
            if norm_w == '.':
                stc = copy.deepcopy(st)
                rcd['wPERst'].append(stc)
                l += 1
                st = {'st_index': l, 'tokens':[]}
        l = 0
        st = {'st_index': l, 'tokens':[]}
        data_out.append(copy.deepcopy(rcd))
        
        
    return data_out



# # 
# def savingdata(fn,o,d,func):
#     import os
#     if os.path.isfile(fn):
#         yn = input('This will overwrite file '+fn+'. Do you want to proceed? Y(es); other character to abort ----   ')
#         if yn == 'Y':
#             with open(fn, o) as f_out:
#                 func(d, f_out)
#         else:
#             print()
#             print('----------- Action Aborted')
# 
#     else:
#         with open(fn, o) as f_out:
#             func(d, f_out)
            

#######################
#### TESTING ##########
#######################

# if __name__ == '__main__':
#     
#     import pickle,json
# 
#    
#     # with open('../data/data_foundjob.pkl', 'rb') as f_in:
#     #     allrecords = pickle.load(f_in)
#     # 
#     # 
#     # fn = '../data/jobproject_forum.json'
#     # o = 'a'
#     # d = allrecords
#     # func = json.dump  
#     # savingdata(fn,o,d,func)
#     
#     with open('../data/jobproject_forum.json', 'r') as f_in:
#         allrecords = json.load(f_in)
#         
#     
#     #allposedsts, forum_ids = allrecordsPreparation(allrecords)
