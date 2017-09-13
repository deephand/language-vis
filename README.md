Here are some datasets & a python script
to examine the character order of words in various languages.

TODO:
-	design a workflow to determine the language of given text
		features to use: totalwordlen, cc, cv, vc, vv, samecc, samevv, more?
		for now, l2 or l1 error function can be used to compare the features above
		works fine for turkish
-	2-grams from wikipedia pages can be used for language training
-	words like i'm, m'appelle or the last word of a sentence (he came.) are discarded
		due to punctuation, this should be handled.
-	design a responsive webpage with a text field & a pie chart
		average word length should be displayed
		pie chart is for cc,cv,vc,vv &
		in cc pie, a samecc pie should be shown (transparent)
		in vv pie, a samevv pie should be shown (transparent)
