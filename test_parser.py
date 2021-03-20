from reTagParser import Parser

def test_parse(parser, inputs, acceptable_outputs):
	if acceptable_outputs == None:
		acceptable_outputs = inputs
	if isinstance(inputs, str):
		inputs = [inputs]
	if isinstance(acceptable_outputs, str):
		acceptable_outputs = [acceptable_outputs]

	for input in inputs:
		output = parser.parse(input)
		if output not in acceptable_outputs:
			print("ERROR")
			print(f"IN {input}")
			print(f"OUT {output}")

###################
# MD 2 BBCODE
###################

def render_italic(value, om, cm):
	return f'[i]{value}[/i]'

parser = Parser()
parser.declare(Parser.SubParser('||', '||', lambda value, om, cm: f'[ispoiler]{value}[/ispoiler]'))
parser.declare(Parser.SubParser('___', '___', lambda value, om, cm: f'[i][u]{value}[/u][/i]'))
parser.declare(Parser.SubParser('__', '__', lambda value, om, cm: f'[u]{value}[/u]'))
parser.declare(Parser.SubParser('_', '_', render_italic, requires_boundary=True))
parser.declare(Parser.SubParser('*', '*', render_italic, allows_space=False))
parser.declare(Parser.SubParser('**', '**', lambda value, om, cm: f'[b]{value}[/b]'))
parser.declare(Parser.SubParser('***', '***', lambda value, om, cm: f'[i][b]{value}[/b][/i]'))
parser.declare(Parser.SubParser('`', '`', lambda value, om, cm: f'[icode]{value}[/icode]', parse_value=False))
# escaping
parser.declare(Parser.SubParser('\\*', '', lambda value, om, cm: f'*{value}'))

# this paragraph is re-used in reverse in bbcode 2 md
test_parse(parser, "test_toaster|| test__toaster", None)
test_parse(parser, "test||toaster_ test||toaster", "test[ispoiler]toaster_ test[/ispoiler]toaster")
test_parse(parser, "test||toaster_ *krr* test||toa__st__er", "test[ispoiler]toaster_ [i]krr[/i] test[/ispoiler]toa[u]st[/u]er")
test_parse(parser, "test `toaster_ *krr* test`toaster **bll**", "test [icode]toaster_ *krr* test[/icode]toaster [b]bll[/b]")
test_parse(parser, "_bll_", "[i]bll[/i]")
test_parse(parser, "*bll*", "[i]bll[/i]")
test_parse(parser, "**bll*", ["*[i]bll[/i]", "[i]*bll[/i]"]) # first one would be correct, second one is "wrong but not a big deal"
test_parse(parser, "*bll**", ["*bll**", "[i]bll[/i]*"]) # first one is discord, second one is riot/element
test_parse(parser, "test * bll * test", None)
test_parse(parser, "test *__bll__* test", "test [i][u]bll[/u][/i] test")
test_parse(parser, "test ___bll___ test", ["test [i][u]bll[/u][/i] test", "test [u][i]bll[/i][/u] test"])
test_parse(parser, "test ***bll*** test", ["test [i][b]bll[/b][/i] test", "test [b][i]bll[/i][/b] test"])

test_parse(parser, "test \\***bll*** test", "test *[b]bll[/b]* test")
test_parse(parser, "test *\\**bll*** test", "test [i]**bll[/i]** test")

print("end test md2bbcode")

###################
# BBCODE 2 MD
###################

def render_quote(value, om, cm):
	nl = '\n' # can't use it in f-strings
	return f"{nl.join([f'> {l}' for l in value.split(nl)])}{nl}— {om.group('author')}{nl}"

parser = Parser()
parser.declare(Parser.SubParser('[ispoiler]', '[/ispoiler]', lambda value, om, cm: f'||{value}||'))
parser.declare(Parser.SubParser('[u]', '[/u]', lambda value, om, cm: f'__{value}__'))
parser.declare(Parser.SubParser('[i]', '[/i]', lambda value, om, cm: f'_{value}_', requires_boundary=True))
parser.declare(Parser.SubParser('[i]', '[/i]', lambda value, om, cm: f'*{value}*', allows_space=False))
parser.declare(Parser.SubParser('[b]', '[/b]', lambda value, om, cm: f'**{value}**'))
parser.declare(Parser.SubParser('[icode]', '[/icode]', lambda value, om, cm: f'`{value}`'))

parser.declare(Parser.SubParser(r'\[url=(?P<url>.*?)]', r'\[\/url]', lambda value, om, cm: f'[{value}]({om.group("url")})', escape_in_regex=False))
parser.declare(Parser.SubParser(r'\[quote=(?P<author>.*?)]', r'\[\/quote]', render_quote, escape_in_regex=False))

# this paragraph is basically the same as in "md 2 bbcode" but reversed
test_parse(parser, "test_toaster[ispoiler] test[u]toaster", None)
test_parse(parser, "test[ispoiler]toaster_ test[/ispoiler]toaster", "test||toaster_ test||toaster")
test_parse(parser, "test[ispoiler]toaster_ [i]krr[/i] test[/ispoiler]toa[u]st[/u]er", "test||toaster_ *krr* test||toa__st__er")
test_parse(parser, "test [icode]toaster_ *krr* test[/icode]toaster [b]bll[/b]", "test `toaster_ *krr* test`toaster **bll**")
test_parse(parser, "[i]bll[/i]", "*bll*")
test_parse(parser, ["*[i]bll[/i]", "[i]*bll[/i]"], "**bll*") # first one would be correct, second one is "wrong but not a big deal"
test_parse(parser, ["*bll**", "[i]bll[/i]*"], "*bll**") # first one is discord, second one is riot/element
test_parse(parser, "test * bll * test", None)
test_parse(parser, "test [i][u]bll[/u][/i] test", "test *__bll__* test")
test_parse(parser, ["test [i][u]bll[/u][/i] test", "test [u][i]bll[/i][/u] test"], ["test *__bll__* test", "test __*bll*__ test"])
test_parse(parser, ["test [i][b]bll[/b][/i] test", "test [b][i]bll[/i][/b] test"], "test ***bll*** test")

# more specific tests
test_parse(parser, "[url=http://test.com]test_toaster[/url]", "[test_toaster](http://test.com)")
test_parse(
	parser,
	"[quote=LeGmask]Bon je retourne manger\nRepas à base de pain aujourd'hui[/quote]test",
	"> Bon je retourne manger\n> Repas à base de pain aujourd'hui\n— LeGmask\ntest"
)

print("end test bbcode2md")
