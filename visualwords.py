import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

languages = ['de', 'en', 'es', 'fi', 'fr', 'id', 'it', 'ms', 'nl', 'pt', 'sv', 'tr']
languages = ['de','en','fr','nl','tr']
dataset_folder = 'dataset/'


vowels = set(['a','e','i','ı','u','ü','o','ö','ä','å','é','è','ê','ë','î','ï','ô','œ',
			'ù','ú','û','æ','â','à','ã','ì','í','ò','ó','õ'])
consonants = set(['b','c','d','f','g','h','j','k','l','m','n','p','q','r','s','t','v'
				'w','x','y','z','ß','ñ','ÿ','ğ','ş','ç'])
all_letters = set()
vowels_de = set(['a','e','i','u','o','ü','ä','ö','ü'])
consonants_de = set(['b','c','d','f','g','h','j','k','l','m','n','p','q','r','s','t','v','w','x','y','z','ß'])
vowels_en = set(['a','e','i','u','o'])
consonants_en = set(['b','c','d','f','g','h','j','k','l','m','n','p','q','r','s','t','v','w','x','y','z'])
vowels_tr = set(['a','e','i','u','o','ı','ü','ö','â','û','î'])
consonants_tr = set(['b','c','d','f','g','h','j','k','l','m','n','p','r','s','t','v','y','z','ç','ğ','ş'])
vowels_nl = set(['a','e','i','u','o','ë'])
consonants_nl = set(['b','c','d','f','g','h','j','k','l','m','n','p','q','r','s','t','v','w','x','y','z'])
vowels_fr = set(['a','e','i','u','o','æ','â','à','é','è','ê','ë','î','ï','ô','œ',
			'ù','û','ü'])
consonants_fr = set(['b','c','d','f','g','h','j','k','l','m','n','p','q','r','s','t','v','w','x','y','z','ç','ÿ'])
consonants = {}
consonants[languages[0]] = consonants_de
consonants[languages[1]] = consonants_en
consonants[languages[2]] = consonants_fr
consonants[languages[3]] = consonants_nl
consonants[languages[4]] = consonants_tr
vowels = {}
vowels[languages[0]] = vowels_de
vowels[languages[1]] = vowels_en
vowels[languages[2]] = vowels_fr
vowels[languages[3]] = vowels_nl
vowels[languages[4]] = vowels_tr


def readFiles(languages):
	dataFrames = {}
	for language in languages:
		dataFrame = pd.read_csv(dataset_folder+language+'.txt',
							sep =' ', header=None, names=['count'], index_col=0)
		#dataFrame = dataFrame.iloc[0:100000,:]
		dataFrames[language] = dataFrame
	return dataFrames


def remove_intruders(dataFrames):
	for language in dataFrames:
		#print(vowels[language]+consonants[language])
		bad_words = [word for word in list(dataFrames[language].index) if
		 			 not set(str(word)).issubset(set(list(vowels[language]) + list(consonants[language])))]
		dataFrames[language].drop(bad_words, inplace=True, axis=0)
		#print(bad_words)
	return dataFrames


def calculate_features(dataFrames):
	features = {}
	for language in dataFrames:
		features[language] = np.zeros(6)
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
			#print(word, cnts, sum(word_convert2), sum(word_convert3))
		print(language, ': ', features[language], ' length: ', sum(features[language]),
				' normalised: ', features[language] / sum(features[language]))

dataFrames = readFiles(languages)
dataFrames = remove_intruders(dataFrames)
calculate_features(dataFrames)
