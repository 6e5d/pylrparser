# example, simple calculator

from .parser import Parser

rules = '''[
[S [next expr4]]
[expr4
	[. expr3]
	[bin.add expr4 "+" expr3]
	[bin.sub expr4 "-" expr3]
]
[expr3
	[, expr2]
	[bin.mul expr3 "*" expr2]
	[bin.div expr3 "/" expr2]
	[bin.mod expr3 "%" expr2]
]
[expr2
	[, pexp]
	[sign.pos "+" pexp]
	[sign.neg "-" pexp]
]
[pexp
	[, "n"]
	[paren "(" expr4 ")"]
]
]'''

class Calc:
	def __init__(self):
		self.parser = Parser(rules)
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
