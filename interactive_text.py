import argparse
import pandas as pd
from dataset_functions import *
from text_functions import *

text = ""
CONSOLE_WIDTH = 170
WORD_COUNT = 200000
languages = ['de','en','fr','nl','tr']

if __name__ == "__main__":

	parser = argparse.ArgumentParser()
	parser.add_argument("-r", "--refresh", help="refresh data cache",
                    action="store_true")
	args = parser.parse_args()

	pd.set_option('display.width', CONSOLE_WIDTH)

	print("setting characters...")
	consonants, vowels = set_characters(languages, True)
	print("reading datasets...")
	dataFrames = read_files(languages, word_count=WORD_COUNT, refresh_cache=args.refresh)
	print("removing erroneous words...")
	dataFrames = remove_intruders_all(dataFrames, consonants, vowels)
	print("calculating 2-gram and 3-gram features of the dataset...")
	df = calculate_features_all(dataFrames, consonants, vowels, refresh_cache=args.refresh)
	df_n = normalize_toall(df)
	while text != "q":
		text = input("Enter a text, q to exit: ")
		if text is "q":
			break
		print("calculating 2-gram features of the input text...")
		str_features = calculate_str_features(text, consonants, vowels, languages)
		print(df_n.iloc[:,0:15], '\n')
		print(str_features.iloc[:,0:15], '\n')
		val = evaluate(str_features, df_n)
		print("Errors:", sorted(list(zip(languages,val)),key=lambda item: item[1]))
