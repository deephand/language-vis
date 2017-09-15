import pandas as pd
import numpy as np
import pickle
import os.path


#dataset source: https://invokeit.wordpress.com/frequency-word-lists/
#languages = ['de', 'en', 'es', 'fi', 'fr', 'id', 'it', 'ms', 'nl', 'pt', 'sv', 'tr']
##currently available languages:
languages = ['de','en','fr','nl','tr']
WORD_COUNT = 200000					#set -1 to parse all words
dataset_folder = 'dataset/'
columns = ['cc', 'cv', 'vc', 'vv', 'samecc', 'samevv',
			'ccc', 'ccv', 'cvc', 'cvv', 'vcc', 'vcv', 'vvc', 'vvv',
			'avgwordlen', 'wordcnt']

##set_characters function:
#use this function to generate consonants & vowels for languages
#before adding a new language, add the language's consonants and vowels
#in the sets 'consonants' and 'vowels'
#to use the same vowels & consonants in all languages
#call the function with lang_by_lang = False
def set_characters(languages, lang_by_lang = True):
	consonants = {}
	vowels = {}
	vowels['de'] =      set(['a','e','i','u','o','ü','ä','ö','ü'])
	consonants['de'] =  set(['b','c','d','f','g','h','j','k','l','m',
						  	 'n','p','q','r','s','t','v','w','x','y',
						  	 'z','ß'])
	vowels['en'] = 	 	set(['a','e','i','u','o'])
	consonants['en'] =  set(['b','c','d','f','g','h','j','k','l','m',
						  	 'n','p','q','r','s','t','v','w','x','y',
						  	 'z'])
	vowels['tr'] = 	 	set(['a','e','i','u','o','ı','ü','ö','â','û',
						  	 'î'])
	consonants['tr'] =  set(['b','c','d','f','g','h','j','k','l','m',
						  	 'n','p','r','s','t','v','y','z','ç','ğ',
						  	 'ş'])
	vowels['nl'] = 	 	set(['a','e','i','u','o','ë'])
	consonants['nl'] =  set(['b','c','d','f','g','h','j','k','l','m',
						  	 'n','p','q','r','s','t','v','w','x','y',
						  	 'z'])
	vowels['fr'] = 	 	set(['a','e','i','u','o','æ','â','à','é','è',
						  	 'ê','ë','î','ï','ô','œ','ù','û','ü'])
	consonants['fr'] =  set(['b','c','d','f','g','h','j','k','l','m',
						  	 'n','p','q','r','s','t','v','w','x','y',
						  	 'z','ç','ÿ'])
	if not lang_by_lang:
		consonants_all = []
		vowels_all = []
		for language in languages:
			consonants_all = consonants_all + list(consonants[language])
			vowels_all = vowels_all + list(vowels[language])
		consonants_all = set(consonants_all)
		vowels_all = set(vowels_all)
		for language in languages:
			consonants[language] = consonants_all
			vowels[language] = vowels_all
	return consonants, vowels


##read_files function:
#given all the languages, reads the word list in the dataset folder
#returns dataFrames with the first WORD_COUNT words for every language
#words as index and counts in count column
def read_files(languages, refresh_cache = False):
	if not os.path.isfile(dataset_folder+"dataframes.p") or refresh_cache:
		dataFrames = {}
		for language in languages:
			dataFrame = pd.read_csv(dataset_folder+language+'.txt',
								sep =' ', header=None, names=['count'], index_col=0)
			dataFrame = dataFrame.iloc[0:WORD_COUNT,:]
			dataFrames[language] = dataFrame
		pickle.dump(dataFrames, open(dataset_folder+"dataframes.p", "wb" ))
	else:
		print('cache found for the files')
		dataFrames = pickle.load(open(dataset_folder+"dataframes.p", "rb" ))

	return dataFrames


##remove_intruders function:
#removes any word in dataFrames which contains a character that is not in
#consonants or vowels of that language
def remove_intruders(dataFrame, consonants, vowels):
	bad_words = [word for word in list(dataFrame.index) if
	 			 not set(str(word)).issubset(set(list(vowels) + list(consonants)))]
	df = dataFrame.drop(bad_words, axis=0)
	return df

def remove_intruders_all(dataFrames, consonants, vowels):
	for language in dataFrames:
		#print(vowels[language]+consonants[language])
		dataFrames[language] = remove_intruders(dataFrames[language], consonants[language],
												vowels[language])
		#print(bad_words)
	return dataFrames


##calculate_features function:
#calculates the number of concurrences of 2-grams
#consonant after consonant(0), consonant after vowel(1), etc
#same consonants(4), same vowels(5)
def calculate_features(dataFrame, consonants, vowels, language):
	feature_list = np.zeros(16)
	words = dataFrame.index.values
	for word in words:
		word = str(word)
		word_bool = [int(char in vowels) for char in list(word)]
		word_convert_2 = np.array([word_bool[idx] * 2 + word_bool[idx + 1] for
										idx in range(len(word_bool) - 1)])
		word_convert_3 = np.array([word_bool[idx]*4 + word_bool[idx+1]*2 + \
		 								word_bool[idx+2] for idx in range(len(word_bool) - 2)])
		word_convert_samevv = np.array([word[idx] == word[idx+1] for idx in range(len(word) - 1)
									if word[idx] in vowels])
		word_convert_samecc = np.array([word[idx] == word[idx+1] for idx in range(len(word) - 1)
									if word[idx] in consonants])
		cnts_2 = np.array([sum(word_convert_2 == i) for i in range(4)])
		cnts_3 = np.array([sum(word_convert_3 == i) for i in range(8)])
		feature_list[:4] = feature_list[:4] + cnts_2
		feature_list[4] = feature_list[4] + sum(word_convert_samevv)
		feature_list[5] = feature_list[5] + sum(word_convert_samecc)
		feature_list[6:14] = feature_list[6:14] + cnts_3
		feature_list[14] = feature_list[14] + len(word)
		#print(word, cnts, sum(word_convert2), sum(word_convert3))
	feature_list[15] = len(words)
	dataFrame_one = pd.DataFrame(data=[feature_list],
								index=[language],
								columns=columns)
	return dataFrame_one

def calculate_features_all(dataFrames, consonants, vowels, refresh_cache = False):
	if not os.path.isfile(dataset_folder+"features.p") or refresh_cache:
		frames = [calculate_features(dataFrames[language], consonants[language],
					vowels[language], language) for	language in dataFrames]
		dataFrame_cv = pd.concat(frames)
		pickle.dump(dataFrame_cv, open(dataset_folder+"features.p", "wb" ))
	else:
		print('cache found for the features')
		dataFrame_cv  = pickle.load(open(dataset_folder+"features.p", "rb" ))
	return dataFrame_cv


##normalize_toall function:
#2-grams are either cc,cv,vc or vv; they are normalized to sum of all
#some 2-grams may be same character (samecc or samevv);
#they are normalized to the sum of cc,cv,vc,vv
def normalize_toall(df):
	df_n = pd.DataFrame(df, copy=True)
	#normalize 2-grams
	df_n.iloc[:,4:6] = df_n.iloc[:,4:6].div(df_n.iloc[:,0:4].sum(axis=1), axis=0)
	df_n.iloc[:,0:4] = df_n.iloc[:,0:4].div(df_n.iloc[:,0:4].sum(axis=1), axis=0)
	#normalize 3-grams
	df_n.iloc[:,6:14] = df_n.iloc[:,6:14].div(df_n.iloc[:,6:14].sum(axis=1), axis=0)
	#average word length
	df_n.iloc[:,14] = df_n.iloc[:,14].div(df_n.iloc[:,15], axis=0)
	return df_n
