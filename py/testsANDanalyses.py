import sys, os

from dotenv import load_dotenv
load_dotenv(dotenv_path='../.env')
load_dotenv()

import pickle, json
import time
import processingData
import collections, itertools, copy, operator


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
#fn = processingData.jsonbuilding(al, nor, fd)

#print(sorted(all_fd.items(), key=lambda x: x[1], reverse=True)[round(len(all_fd)/50):round(len(all_fd)/50)+10+1])

opacity, sizing, enlargedopacity = processingData.metrics_test(al, nor, fd)