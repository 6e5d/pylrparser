import json

from . import align_output
from .lrparser import LrParser
from .rule import load_rules
from .build import Lr1Builder

class ParserConfig:
	def __init__(self):
		self.action = None
		self.goto = None
		self.rules = None
		self.term = None
		self.nonterm = None
		self.names = None
	def load_string(self, rule_string):
		term, nonterm, rules, names = load_rules(rule_string)
		builder = Lr1Builder(rules, term, nonterm)
		self.action, self.goto = builder.build()
		self.rules = rules
		self.term = term
		self.nonterm = nonterm
		self.names = names
	def load_cache(self, path):
		with open(path) as f:
			[
				self.action,
				self.goto,
				self.rules,
				self.term,
				self.nonterm,
				self.names,
			] = json.loads(f.read())
	def save(self, path):
		s = json.dumps([
			self.action,
			self.goto,
			self.rules,
			self.term,
			self.nonterm,
			self.names,
		])
		with open(path, "w") as f:
			print(s, file = f)

class Parser:
	def __init__(self, pc):
		self.parser = LrParser(
			pc.action,
			pc.goto,
			pc.term,
			pc.rules,
			pc.nonterm,
		)
		self.names = pc.names
	def parse(self, toks, orig):
		self.parser.reset()
		(ret, idx) = self.parser.parse(toks + ["$"])
		if ret != "ok":
			print(" ".join(orig[:idx]))
			raise Exception(ret)
		output = self.parser.output
		output = align_output(output, orig, self.names)
		return output

def cached_parser(rule_file, cache_file):
	pc = ParserConfig()
	if not cache_file.exists() or\
		cache_file.stat().st_mtime < rule_file.stat().st_mtime:
		s = open(rule_file, "r").read()
		pc.load_string(s)
		pc.save(cache_file)
	else:
		pc.load_cache(cache_file)
	return Parser(pc)
