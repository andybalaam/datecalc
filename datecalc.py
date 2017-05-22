from collections import namedtuple
from datetime import date
import sys


try:
    input = raw_input
except:
    pass


WordToken = namedtuple("WordToken", ["word"])
NumberToken = namedtuple("NumberToken", ["number"])
WordTree = namedtuple("WordTree", ["word"])
LengthTree = namedtuple("LengthTree", ["length", "unit"])
DateValue = namedtuple("DateValue", ["value"])
LengthValue = namedtuple("LengthValue", ["length"])


def make_token(ch):
    if ch[0] in "0123456789":
        return NumberToken(ch)
    else:
        return WordToken(ch)


def lex(chars):
    return [make_token(ch) for ch in chars.split(" ")]


def parse(chars):
    tokens = lex(chars)
    if type(tokens[0]) == NumberToken:
        return [LengthTree(tokens[0], tokens[1])]
    else:
        return [WordTree(tokens[0])]


def length_tree_in_days(length_tree):
    if length_tree.unit.word == "weeks":
        return int(length_tree.length.number) * 7
    else:
        return int(length_tree.length.number)


def evaluate(chars):
    trees = parse(chars)
    if type(trees[0]) == LengthTree:
        return [LengthValue(length_tree_in_days(trees[0]))]
    else:
        return [DateValue(date.today())]


def pretty(value):
    if type(value) == DateValue:
        return value.date.strfdate("%y-%m-%d (%W)")
    else:
        return "%s days" % value.length


assert lex("today") == [WordToken("today")]
assert lex("2 days") == [NumberToken("2"), WordToken("days")]
assert lex("3 weeks") == [NumberToken("3"), WordToken("weeks")]


assert parse("today") == [WordTree(WordToken("today"))]
assert parse("2 days") == [LengthTree(NumberToken("2"), WordToken("days"))]
assert parse("3 weeks") == [LengthTree(NumberToken("3"), WordToken("weeks"))]


assert evaluate("today") == [DateValue(date.today())]
assert evaluate("2 days") == [LengthValue(2)]
assert evaluate("3 weeks") == [LengthValue(21)]


for arg in sys.argv[1:]:
    print(" ".join(pretty(v) for v in evaluate(arg)))


#for ln in sys.stdin:
#    for v in evaluate(ln[:-1]):
#        pass
#    print(pretty(v))
