class LrParser:
	def __init__(self, action, goto, toksym, rules, rulesym):
		# print(action, goto, toksym)
		self.action = action
		self.toksym = toksym
		self.goto = goto
		self.rulesym = rulesym
		self.rules = rules
		self.reset()
	def reset(self):
		self.stst = [0]
		self.stack = []
		self.output = []
	def pop(self, l):
		assert len(self.stst) >= l + 1
		assert len(self.stack) >= l
		if l == 0:
			return []
		stack = self.stack[-l:]
		self.stst = self.stst[:-l]
		self.stack = self.stack[:-l]
		return stack
	def update_output(self, s, ruleid):
		s = list(s)
		output2 = []
		for idx, ss in reversed(list(enumerate(s))):
			if ss in self.rulesym:
				p = self.output.pop()
				s[idx] = p
		self.output.append([ruleid] + s)
	def go(self, s):
		col = self.toksym.index(s)
		row = self.stst[-1]
		if row < 0:
			return "minusrow"
		op = self.action[row][col]
		if op == True:
			return "finish"
		if op == None:
			print("ERROR", row, self.toksym[col])
			return "errorstate"
		if op[0] == "s":
			self.stack.append(s)
			self.stst.append(op[1])
			return "shift"
		assert op[0] == "r"
		# reduce
		op = op[1]
		name, generation = self.rules[op]
		col = self.rulesym.index(name)
		stack = self.pop(len(generation))
		self.update_output(stack, op)
		if stack != generation:
			raise Exception(stack, generation)
		state = self.goto[self.stst[-1]][col]
		if state < 0:
			print(self.goto, self.stst[-1], col, self.rulesym[col])
			return "errorgoto"
		self.stack.append(name)
		self.stst.append(state)
		return "reduce"
	def parse(self, toks):
		idx = 0
		while True:
			view = toks[idx]
			# print("go", view, self.stst, self.stack, end = " ")
			ret = self.go(view)
			# print(ret)
			match ret:
				case "finish":
					self.output = [0] + self.output
					break
				case "shift":
					idx += 1
				case "reduce":
					continue
				case e:
					return (e, idx)
		return ("ok", idx)
