# example, simple calculator

from pathlib import Path
from .parser import cached_parser

class Calc:
	def __init__(self):
		self.parser = cached_parser(
			Path(__file__).parent / "calc.txt",
			Path(__file__).parent / "calc.json",
		)
	def tokenize(self, s):
		idx = 0
		s = list(s)
		output = []
		output_ty = []
		while idx < len(s):
			if s[idx].isspace():
				continue
			if s[idx].isdigit():
				num = ""
				while s[idx].isdigit():
					num += s[idx]
					idx += 1
					if idx >= len(s):
						break
				output.append(num)
				output_ty.append("n")
				continue
			output.append(s[idx])
			output_ty.append(s[idx])
			idx += 1
		return output, output_ty
	def eval(self, expr):
		if isinstance(expr, str):
			if expr.isnumeric():
				return int(expr)
			else:
				return expr
		print(expr)
		match expr[0]:
			case "bin.add":
				return int(self.eval(expr[1])) +\
					int(self.eval(expr[3]))
			case "bin.sub":
				return int(self.eval(expr[1])) -\
					int(self.eval(expr[3]))
			case "bin.mul":
				return int(self.eval(expr[1])) *\
					int(self.eval(expr[3]))
			case "bin.div":
				return int(self.eval(expr[1])) //\
					int(self.eval(expr[3]))
			case "bin.mod":
				return int(self.eval(expr[1])) %\
					int(self.eval(expr[3]))
			case "sign.neg":
				return -self.eval(expr[2])
			case "sign.pos":
				return self.eval(expr[2])
			case "paren":
				return self.eval(expr[2])
			case x:
				return self.eval(expr[1])
	def calc(self, s):
		s, sty = self.tokenize(s)
		output = self.parser.parse(sty, s)
		return self.eval(output)
