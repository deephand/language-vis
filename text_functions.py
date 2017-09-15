import numpy as np
import pandas as pd
from dataset_functions import calculate_features, normalize_toall,remove_intruders

##calculate_str_features function:
#this function returns the normalized features in all languages of a given text
def calculate_str_features(text, consonants, vowels, languages):
	word_counts = {}
	words = text.split(sep=' ')
	for word in words:
		if word in word_counts:
			word_counts[word] += 1
		else:
			word_counts[word] = 1
	df = pd.DataFrame.from_dict(word_counts, orient='index')
	df = df.rename(columns={0: 'count'})
	features_list = [calculate_features(
						remove_intruders(df,consonants[language], vowels[language]),
						consonants[language],
						vowels[language],
						language) for language in languages]
	features = pd.concat(features_list)
	features = normalize_toall(features)
	return features


##error function l2
def err_l2(mx1, mx2):
	return np.sum(np.power((mx1 - mx2), 2), axis=1)

##error function l1
def err_l1(mx1, mx2):
	return np.sum(np.absolute((mx1 - mx2)), axis=1)

##evaluate function:
#the first six functions are used for evaluation without weighting
def evaluate(str_features, language_features, evalfun = err_l2):
	mx1 = np.array(str_features.iloc[:,0:6])
	mx2 = np.array(language_features.iloc[:,0:6])
	return evalfun(mx1, mx2)
