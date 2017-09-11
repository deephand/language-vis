import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

#dataset source: https://invokeit.wordpress.com/frequency-word-lists/
#languages = ['de', 'en', 'es', 'fi', 'fr', 'id', 'it', 'ms', 'nl', 'pt', 'sv', 'tr']
##currently available languages:
languages = ['de','en','fr','nl','tr']
dataset_folder = 'dataset/'
WORD_COUNT = 100000						#set -1 to parse all words


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
def read_files(languages):
	dataFrames = {}
	for language in languages:
		dataFrame = pd.read_csv(dataset_folder+language+'.txt',
							sep =' ', header=None, names=['count'], index_col=0)
		dataFrame = dataFrame.iloc[0:WORD_COUNT,:]
		dataFrames[language] = dataFrame
	return dataFrames


##remove_intruders function:
#removes any word in dataFrames which contains a character that is not in
#consonants or vowels of that language
def remove_intruders(dataFrames, consonants, vowels):
	for language in dataFrames:
		#print(vowels[language]+consonants[language])
		bad_words = [word for word in list(dataFrames[language].index) if
		 			 not set(str(word)).issubset(set(list(vowels[language]) + list(consonants[language])))]
		dataFrames[language].drop(bad_words, inplace=True, axis=0)
		#print(bad_words)
	return dataFrames



##calculate_features function:
#calculates the number of concurrences of 2-grams
#consonant after consonant(0), consonant after vowel(1), etc
#same consonants(4), same vowels(5)
def calculate_features(dataFrames, consonants, vowels):
	features = {}
	for language in dataFrames:
		features[language] = np.zeros(8)
		dataFrame = dataFrames[language]
		words = dataFrame.index.values
		for word in words:
			word = str(word)
			word_bool = [int(char in vowels[language]) for char in list(word)]
			word_convert = np.array([word_bool[idx] * 2 + word_bool[idx + 1] for
											idx in range(len(word_bool) - 1)])
			word_convert2 = np.array([word[idx] == word[idx+1] for idx in range(len(word) - 1)
										if word[idx] in vowels[language]])
			word_convert3 = np.array([word[idx] == word[idx+1] for idx in range(len(word) - 1)
										if word[idx] in consonants[language]])
			cnts = np.array([sum(word_convert == i) for i in range(4)])
			features[language][:4] = features[language][:4] + cnts
			features[language][4] = features[language][4] + sum(word_convert2)
			features[language][5] = features[language][5] + sum(word_convert3)
			features[language][6] = features[language][6] + len(word)
			#print(word, cnts, sum(word_convert2), sum(word_convert3))
		features[language][7] = len(words)
		print('language ' + language + ' completed.')
	dataFrame_cv = pd.DataFrame(data=list(features.values()),
								index=features.keys(),
								columns=['cc', 'cv', 'vc', 'vv', 'samevv',
										 'samecc','totalwordlen','wordcnt'])
	return dataFrame_cv

##normalize_toall function:
#2-grams are either cc,cv,vc or vv; they are normalized to sum of all
#some 2-grams may be same character (samecc or samevv);
#they are normalized to the sum of cc,cv,vc,vv
def normalize_toall(df):
	df_n = pd.DataFrame(df, copy=True)
	df_n.iloc[:,4:6] = df_n.iloc[:,4:6].div(df_n.iloc[:,0:4].sum(axis=1), axis=0)
	df_n.iloc[:,0:4] = df_n.iloc[:,0:4].div(df_n.iloc[:,0:4].sum(axis=1), axis=0)
	df_n.iloc[:,6] = df_n.iloc[:,6].div(df_n.iloc[:,7], axis=0)
	return df_n


consonants, vowels = set_characters(languages, True)
dataFrames = read_files(languages)
dataFrames = remove_intruders(dataFrames, consonants, vowels)
df = calculate_features(dataFrames, consonants, vowels)
df_n = normalize_toall(df)
print(df_n)
