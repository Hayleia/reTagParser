import re

class Parser:
	class SubParser:
		def __init__(self, opening, closing, renderer, requires_boundary=False, allows_space=True, parse_value=True, escape_in_regex=True):
			self.opening = opening
			self.closing = closing
			self.bound = r'\b' if requires_boundary else ''
			self.space = r'\S' if not allows_space else ''
			# WARNING the above makes the opening and closing strings eat one character each!!!
			# the value should get these characters back or it will render nesting impossible
			# hence the groups in regex so we can read/skip what we want
			self.opening_rx = re.compile(fr'(?P<prefix>{self.bound})(?P<opening>{re.escape(opening) if escape_in_regex else opening}){self.space}')
			self.closing_rx = re.compile(fr'(?P<prefix>{self.space})(?P<closing>{re.escape(closing) if escape_in_regex else closing}){self.bound}')
			self.renderer = renderer
			self.parse_value = parse_value

	def __init__(self):
		self.sub_parsers = []

	def declare(self, sub_parser):
		self.sub_parsers.append(sub_parser)

	def parse(self, text):
		# find the first opening for every subparser
		open_matches = [(sp, list(sp.opening_rx.finditer(text))) for sp in self.sub_parsers]
		open_matches = [(sp, list_matches[0]) for sp, list_matches in open_matches if len(list_matches) != 0]

		# find the first closing following the opening (find all, filter smaller  ones, filter when there is none)
		indices = [(sp, om, [match for match in sp.closing_rx.finditer(text) if match.start() > om.start()]) for sp, om in open_matches]
		indices = [(sp, om, list_matches[0]) for sp, om, list_matches in indices if len(list_matches) != 0]

		if len(indices) == 0:
			return text

		# sort to easily get the first opening
		indices.sort(key=lambda x: x[1].start())
		# filter and keep only openings that start at the same spot as the first opening (because there might be a match for '_' and '__')
		indices = [(sp, om, cm) for sp, om, cm in indices if om.start() == indices[0][1].start()]
		# get the longest one
		indices.sort(key=lambda x: len(x[0].opening))
		sp, om, cm = indices[-1]

		value = text[om.start()+len(om.group('opening')):cm.start()+len(cm.group('prefix'))]
		if sp.parse_value:
			value = self.parse(value)

		return f"{text[:om.start()]}{sp.renderer(value, om, cm)}{self.parse(text[cm.start()+len(cm.group('prefix'))+len(cm.group('closing')):])}"
