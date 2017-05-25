all: test

test:
	echo "today" | python2 datecalc.py
	echo "today" | python3 datecalc.py
