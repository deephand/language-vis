import argparse
from dataset_functions import *
import matplotlib.pyplot as plt
import matplotlib

languages = ['de', 'en', 'fr', 'nl', 'tr']

if __name__ == "__main__":

	parser = argparse.ArgumentParser()
	parser.add_argument("-r", "--refresh", help="refresh data cache",
                    action="store_true")
	args = parser.parse_args()

	consonants, vowels = set_characters(languages, True)

	dataFrames = read_files(languages, refresh_cache=args.refresh)
	dataFrames = remove_intruders_all(dataFrames, consonants, vowels)

	df = calculate_features_all(dataFrames, consonants, vowels, refresh_cache=args.refresh)
	df_n = normalize_toall(df)

	print(df)
	print(df_n)

	plt.style.use('ggplot')
	for i in range(len(languages)):
		labels = ['consonant-consonant', 'consonant-vowel',
					'vowel-consonant', 'vowel-vowel']
		explode = [0.01] * len(labels)
		fig, ax = plt.subplots()
		ax.pie(df_n.iloc[i,0:4] * 100, labels=labels, explode=explode,
				autopct="%1.1f%%")
		plt.title(languages[i])
		ax.axis('equal')
		plt.show()
