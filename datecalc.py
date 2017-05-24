from collections import namedtuple
from datetime import date, timedelta
import sys


WordToken = namedtuple("WordToken", ["word"])
NumberToken = namedtuple("NumberToken", ["number"])
OperatorToken = namedtuple("OperatorToken", ["name", "tag"])
WordTree = namedtuple("WordTree", ["word"])
LengthTree = namedtuple("LengthTree", ["length", "unit"])
OperatorTree = namedtuple("OperatorTree", ["operator", "left", "right"])
DateValue = namedtuple("DateValue", ["value"])
LengthValue = namedtuple("LengthValue", ["length"])


def make_token(ch):
    if ch[0] in "0123456789":
        return NumberToken(ch)
    elif ch[0] in "+":
        return OperatorToken(ch[0], ch[0])
    else:
        return WordToken(ch)


def lex(chars):
    if len(chars) == 0:
        return []
    else:
        return [make_token(ch) for ch in chars.split(" ")]


def parse(tokens, so_far=None):
    if len(tokens) == 0:
        return so_far
    elif type(tokens[0]) == NumberToken:
        return LengthTree(tokens[0], tokens[1])
    elif type(tokens[0]) == OperatorToken:
        return OperatorTree(tokens[0], so_far, parse(tokens[1:]))
    else:
        return parse(tokens[1:], WordTree(tokens[0]))


def length_tree_in_days(length_tree):
    unit = length_tree.unit.word
    if unit in ("weeks", "week"):
        return int(length_tree.length.number) * 7
    elif unit in ("days", "day"):
        return int(length_tree.length.number)
    else:
        raise Exception("Unknown time unit '%s'." % unit)


def evaluate(tree):
    if type(tree) == LengthTree:
        return LengthValue(length_tree_in_days(tree))
    elif type(tree) == OperatorTree:
        left = evaluate(tree.left).value
        right = evaluate(tree.right).length
        return DateValue(left + timedelta(days=right))
    elif type(tree) == WordTree:
        if tree.word.word == "today":
            return DateValue(date.today())
        elif tree.word.word == "tomorrow":
            return DateValue(date.today() + timedelta(days=1))
        elif tree.word.word == "yesterday":
            return DateValue(date.today() - timedelta(days=1))
        else:
            raise Exception("Unknown word '%s'." % tree.word.word)

    else:
        raise Exception("Unknown tree type '%s'." % type(tree))


def pretty(value):
    if type(value) == DateValue:
        return value.value.strftime("%Y-%m-%d (%A)")
    else:
        return "%s days" % value.length


assert lex("today") == [WordToken("today")]
assert lex("tomorrow") == [WordToken("tomorrow")]
assert lex("2 days") == [NumberToken("2"), WordToken("days")]
assert lex("3 weeks") == [NumberToken("3"), WordToken("weeks")]
assert (
    lex("today + 3 days") ==
    [
        WordToken("today"),
        OperatorToken("+", "+"),
        NumberToken("3"),
        WordToken("days")
    ]
)


assert parse(lex("today")) == WordTree(WordToken("today"))
assert parse(lex("tomorrow")) == WordTree(WordToken("tomorrow"))
assert parse(lex("2 days")) == LengthTree(NumberToken("2"), WordToken("days"))
assert parse(lex("3 weeks")) == LengthTree(NumberToken("3"), WordToken("weeks"))
assert (
    parse(lex("today + 3 days")) ==
    OperatorTree(
        OperatorToken("+", "+"),
        WordTree(WordToken("today")),
        LengthTree(NumberToken("3"), WordToken("days"))
    )
)


assert evaluate(parse(lex("today"))) == DateValue(date.today())
assert (
    evaluate(parse(lex("tomorrow"))) ==
    DateValue(date.today() + timedelta(days=1))
)
assert (
    evaluate(parse(lex("yesterday"))) ==
    DateValue(date.today() - timedelta(days=1))
)
assert evaluate(parse(lex("2 days"))) == LengthValue(2)
assert evaluate(parse(lex("3 weeks"))) == LengthValue(21)
assert (
    evaluate(parse(lex("today + 3 days"))) ==
    DateValue(date.today() + timedelta(days=3))
)
assert (
    evaluate(parse(lex("tomorrow + 1 day"))) ==
    DateValue(date.today() + timedelta(days=2))
)
try:
    evaluate(parse(lex("banana")))
    exc = False
except:
    exc = True
assert exc
try:
    evaluate(parse(lex("1 banana")))
    exc = False
except:
    exc = True
assert exc


# Adjust for your locale
assert pretty(DateValue(date(2017, 5, 23))).startswith("2017-05-23 (")

for arg in sys.argv[1:]:
    print(pretty(evaluate(parse(lex(arg)))))


#for ln in sys.stdin:
#    for v in evaluate(ln[:-1]):
#        pass
#    print(pretty(v))
