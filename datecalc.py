from collections import namedtuple
from datetime import date, timedelta
import sys


def make_token(s):
    if s[0] in "0123456789":
        return ("NumberToken", s)
    elif s[0] in "+":
        return ("OperatorToken", s[0])
    else:
        return ("WordToken", s)


def lex(chars):
    if len(chars) == 0:
        return []
    else:
        return [make_token(s) for s in chars.split(" ")]


def parse(tokens, so_far=None):
    if len(tokens) == 0:
        return so_far
    elif tokens[0][0] == "NumberToken":
        return ("LengthTree", tokens[0][1], tokens[1][1])
    elif tokens[0][0] == "OperatorToken":
        return ("OperatorTree", tokens[0][1], so_far, parse(tokens[1:]))
    else: # Must be WordToken
        return parse(tokens[1:], ("WordTree", tokens[0][1]))


def length_tree_in_days(length_tree):
    unit = length_tree[2]
    number = int(length_tree[1])
    if unit in ("weeks", "week"):
        return number * 7
    elif unit in ("days", "day"):
        return number
    else:
        raise Exception("Unknown time unit '%s'." % unit)


def evaluate(tree):
    if tree[0] == "LengthTree":
        return ("LengthValue", length_tree_in_days(tree))
    elif tree[0] == "OperatorTree":
        left = evaluate(tree[2])[1]
        right = evaluate(tree[3])[1]
        return ("DateValue", left + timedelta(days=right))
    elif tree[0] == "WordTree":
        if tree[1] == "today":
            return ("DateValue", date.today())
        elif tree[1] == "tomorrow":
            return ("DateValue", date.today() + timedelta(days=1))
        elif tree[1] == "yesterday":
            return ("DateValue", date.today() - timedelta(days=1))
        else:
            raise Exception("Unknown word '%s'." % tree[1])

    else:
        raise Exception("Unknown tree type '%s'." % tree[0])


def pretty(value):
    if value[0] == "DateValue":
        return value[1].strftime("%Y-%m-%d (%A)")
    else:
        return "%s days" % value[1]


assert lex("today") == [("WordToken", "today")]
assert lex("tomorrow") == [("WordToken", "tomorrow")]
assert lex("2 days") == [("NumberToken", "2"), ("WordToken", "days")]
assert lex("3 weeks") == [("NumberToken", "3"), ("WordToken", "weeks")]
assert (
    lex("today + 3 days") ==
    [
        ("WordToken", "today"),
        ("OperatorToken", "+"),
        ("NumberToken", "3"),
        ("WordToken", "days")
    ]
)


assert parse(lex("today")) == ("WordTree", "today")
assert parse(lex("tomorrow")) == ("WordTree", "tomorrow")
assert (
    parse(lex("2 days")) ==
    ("LengthTree", "2", "days")
)
assert (
    parse(lex("3 weeks")) ==
    ("LengthTree", "3", "weeks")
)
assert (
    parse(lex("today + 3 days")) ==
    ("OperatorTree",
        "+",
        ("WordTree", "today"),
        ("LengthTree", "3", "days")
    )
)


assert evaluate(parse(lex("today"))) == ("DateValue", date.today())
assert (
    evaluate(parse(lex("tomorrow"))) ==
    ("DateValue", date.today() + timedelta(days=1))
)
assert (
    evaluate(parse(lex("yesterday"))) ==
    ("DateValue", date.today() - timedelta(days=1))
)
assert evaluate(parse(lex("2 days"))) == ("LengthValue", 2)
assert evaluate(parse(lex("3 weeks"))) == ("LengthValue", 21)
assert (
    evaluate(parse(lex("today + 3 days"))) ==
    ("DateValue", date.today() + timedelta(days=3))
)
assert (
    evaluate(parse(lex("tomorrow + 1 day"))) ==
    ("DateValue", date.today() + timedelta(days=2))
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


assert pretty(("DateValue", date(2017, 5, 23))).startswith("2017-05-23 (")
assert pretty(evaluate(parse(lex("2 weeks")))) == "14 days"


for arg in sys.argv[1:]:
    print(pretty(evaluate(parse(lex(arg)))))


while True:
    ln = sys.stdin.readline()
    if ln is None or ln.strip() == "":
        break
    sys.stdout.write("%s\n" % pretty(evaluate(parse(lex(ln.strip())))))
