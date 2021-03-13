# reTagParser

Please read the following sentence until the end. This is a parser for languages with opening and closing tags (such as bbcode) that uses regex BUT it ONLY uses regex to match tags and still parses the string from left to right.

In other words, it does __NOT__ do this.
```python
re.sub(
	r"ORIGINAL_OPENING_TAG(.*)ORIGINAL_CLOSING_TAG",
	r"REPLACEMENT_OPENING_TAG\g<1>REPLACEMENT_CLOSING_TAG",
	s
)
```
This would fail on (stupid) cases such as this one:
```bbcode
test [i]italic thing [b]stuff[/i] etc[/b] whatever
```
Using re.sub the way it was illustrated above, the result would not be the correct result. The correct result should not parse `[b]` and `[/b]` because `[b][/b]` and `[i][/i]` are interweaved but not nested.

Using regex only to parse tags but still parsing in the right order — the way this parser does — rightfully ignores `[b]` in this case.

## Why the project

This project is mostly part of the TI-Planet discord-shoutbox bridge where we need to transform limited markdown into bbcode and conversely.

### Reinventing the wheel

Yes there are already markdown parsers and bbcode parsers. But most of them do not share exactly our purposes which in the end causes more problems for us than reinventing the wheel. For example, most of them have html as the transformation target and we don't. Most of them also have default options that we don't want (as in, that cause problems that we have to work around).

Check out ShoutBot's code where we had problems with the markdown-it lib with spoiler tags, or problems with the bbcode lib with URLs and with stuff that were not tags such as `[[a b][b c]]` (someone talking about matrices) which was somehow interpreted as bold tags, and the issue with "interweaving without nesting" was present.

Finding workarounds/solutions/other_libs for these problems requires time, and reinventing the wheel required less time.

Maybe libs for our exact usecases exist and we can still look for that better solution, but at least we have a working project in the meantime. It is also for this reason that performances are not a high priority issue for this sub-project.

## Known issues/limitations

This only works with things that have an opening and closing tags. For example, it cannot parse this:
```txt
> this is a quote
> a multiline quote even
— Author
```

This also uses the first match as the opening tag. For example here:
```txt
things **bll* stuff
```
In markdown, `*bll*` would need to be interpreted as emphasis, and the first `*` would be out of the emphasis. Using this parser here, the first `*` would be interpreted as the opening tag and the second `*` would be inside the emphasis. Since we only found that problem with `**bll*` and `__bll_` in markdown and the result isn't too far from the correct result, we marked this as low priority issue on an edge case in a grey area (for example Riot/Element and vscode's preview parse `*bll**` but discord does not parse it at all, and `**bll*` looks similar).

## How to use

Example code:
```python
parser = Parser()
parser.declare(Parser.SubParser('||', '||', lambda value, om, cm: f'[ispoiler]{value}[/ispoiler]'))
parser.declare(Parser.SubParser('_', '_', lambda value, om, cm: f'[i]{value}[/i]', requires_boundary=True))

print(parser.parse('an example _sentence to_ parse with ||traps _sometimes|| and_ everything works'))
```
Example output:
```txt
an example [i]]sentence to[/i] parse with [ispoiler]traps _sometimes[/ispoiler] and_ everything works
```

The Parser class has options if spaces are required outside of tags, or if tags are required to be right next to a word without a space in between, or options to specify a regex directly instead of a simple string, or if the text between tags needs to be recursively parsed or left untouched, etc.

Check out `test_parser.py` for uses of these options.
