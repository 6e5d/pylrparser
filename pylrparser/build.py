from itertools import groupby
from . import G
# item = [name [generation] dot_idx ahead]

def tuple2item(t):
	return Item((t[0], list(t[1])), t[2], t[3], t[4])
def item2tuple(t):
	return (t.head, tuple(t.body), t.idx, t.nxt, t.orig)

class Item:
	def __init__(self, rule, idx, nxt, orig):
		self.head = rule[0]
		self.body = rule[1]
		self.idx = idx
		self.nxt = nxt
		self.orig = orig
	def __eq__(self, other):
		if not isinstance(other, Item):
			return False
		if self.head != other.head:
			return False
		if self.body != other.body:
			return False
		if self.idx != other.idx:
			return False
		return self.nxt == other.nxt
	def __repr__(self):
		s = []
		s.append(f"{self.head} → ")
		s.append(" ".join(self.body[:self.idx]))
		s.append(" · ")
		s.append(" ".join(self.body[self.idx:]))
		s.append(", " + str(self.nxt))
		s.append(f" ({self.orig})")
		return "".join(s)

class Lr1Builder:
	def __init__(self, rules, toksym, rulesym):
		self.rules = rules
		self.toksym = toksym
		self.rulesym = rulesym
		self.first = {sym: set() for sym in rulesym}
		self.igroups = []
		self.iglinks = []
		self.igsym = []
		self.build_first()
	def build_first_round2(self, sym, rule):
		if rule[0] != sym:
			return
		if len(rule[1]) == 0:
			self.first[sym].add("%")
			return
		if rule[1][0] in self.toksym:
			self.first[sym].add(rule[1][0])
			return
		for y in rule[1]:
			if "%" not in self.first[y]:
				self.first[sym] |= self.first[y]
				break
			else:
				s = set(self.first[y])
				s.discard("$")
				self.first[sym] |= s
		else:
			self.first[sym] != "%"
	def build_first_round(self):
		for sym in self.rulesym:
			for rule in self.rules:
				self.build_first_round2(sym, rule)
	def build_first(self):
		l = -1
		l2 = 0
		while l2 > l:
			l = l2
			self.build_first_round()
			l2 = sum([len(v) for v in self.first.values()])
	def build_follow_round2(self, item, follows):
		for idx, sym in enumerate(item.body):
			if sym not in self.rulesym:
				continue
			# A = aBb
			if idx == len(item.body) - 1:
				# last, b = eps, follow(B)|=follow(A)
				if sym in self.rulesym:
					follows[sym] |= follows[item.head]
					if item.nxt in self.toksym:
						follows[sym].add(item.nxt)
			else:
				# non last, follow(B)|=first(b)/{eps}
				nxt = item.body[idx + 1]
				if nxt in self.rulesym:
					s = self.first[nxt]
					s.discard("%")
				else:
					s = set([nxt])
				follows[sym] |= s
	def build_follow_round(self, items, follows):
		for item in items:
			self.build_follow_round2(item, follows)
	def build_follow(self, items):
		follows = {sym: set() for sym in self.rulesym}
		follows["S"].add("$")
		l = -1
		l2 = 0
		while l2 > l:
			l = l2
			self.build_follow_round(items, follows)
			l2 = sum([len(v) for v in follows.values()])
		return follows
	def propagate2(self, item, rule, orig):
		assert isinstance(item, Item)
		if item.idx == len(item.body):
			return None
		nxt = item.body[item.idx]
		if rule[0] != nxt:
			return None
		s = Item(rule, 0, None, orig)
		return s
	def propagate(self, items):
		l = 0
		while l < len(items):
			l = len(items)
			for item in items[:l]:
				for (orig, rule) in enumerate(self.rules):
					result = self.propagate2(item, rule,
						orig)
					if result != None:
						if result in items:
							continue
						items.append(result)
		return items
	def combine_ahead(self, items, follows):
		items2 = []
		for item in items:
			for ahead in follows[item.head]:
				i2 = item2tuple(item)
				i2 = tuple2item(i2)
				i2.nxt = ahead
				i2 = item2tuple(i2)
				items2.append(i2)
		return items2
	def forward(self, igroup):
		indices = dict()
		iglink = []
		for t in igroup:
			item = tuple2item(t)
			if item.idx == len(item.body):
				iglink.append(-1)
				continue
			item.idx += 1
			i2 = item2tuple(item)
			nxt = item.body[item.idx - 1] # the jump label
			if nxt not in indices:
				indices[nxt] = len(self.igroups)
				self.igroups.append([])
				self.igsym.append(nxt)
			idx = indices[nxt]
			iglink.append(idx)
			self.igroups[idx].append(i2)
		self.iglinks.append(iglink)
	def delete_igroup(self, idx, to):
		for iglink in self.iglinks[:idx]:
			for idy, t in enumerate(iglink):
				if t > idx:
					iglink[idy] = t - 1
				elif t == idx:
					iglink[idy] = to
		del self.igroups[idx]
		# no need to delete iglinks, it has not been created
	def build_reduce(self, s, f, t, action):
		r = f
		c = self.toksym.index(s[3])
		if s[3] == "$" and s[0] == "S":
			v = 0
		else:
			v = G(s[4])
		# print(r, c, "reduce", v)
		if action[r][c] != -1 and action[r][c] != v:
			raise Exception("amb reduce", r, c, s)
		action[r][c] = v
	def build_goto(self, s, f, t, goto):
		nxt = s[1][s[2]]
		r = f
		c = self.rulesym.index(nxt)
		# print(r, c, "shift", t)
		if goto[r][c] != -1 and goto[r][c] != t:
			raise Exception("amb goto", r, c, t, goto[r][c])
		goto[r][c] = t
		return False
	def build_shift(self, s, f, t, action):
		# return IsFail
		nxt = s[1][s[2]]
		if nxt not in self.toksym:
			return True
		r = f
		c = self.toksym.index(nxt)
		# print(r, c, "shift", t)
		if action[r][c] != -1 and action[r][c] != t:
			raise Exception("amb shift", r, c, s,
				t, action[r][c])
		action[r][c] = t
		return False
	def build2(self):
		# build action and goto
		slen = len(self.igroups)
		action = [[-1 for _ in range(len(self.toksym) ** 2)]
			for _ in range(slen)
		]
		goto = [[-1 for _ in range(len(self.rulesym))]
			for _ in range(slen)
		]
		for f, (group, iglink) in enumerate(
			zip(self.igroups, self.iglinks)
		):
			for (s, t) in zip(group, iglink):
				# print(f, t, s)
				if s[2] == len(s[1]):
					self.build_reduce(s, f, t, action)
				elif self.build_shift(s, f, t, action):
					self.build_goto(s, f, t, goto)
		return action, goto
	def find_collision(self, idx):
		for idy, igroup in enumerate(self.igroups[:idx]):
			if igroup == self.igroups[idx]:
				self.delete_igroup(idx, idy)
				return True
		return False
	def build(self):
		assert self.rules[0][0] == "S"
		item = Item(self.rules[0], 0, "$", 0)
		item = item2tuple(item)
		self.igroups.append([item])
		self.igsym.append(None)
		idx = 0
		while idx < len(self.igroups):
			# print(f"Item group {idx}/{len(self.igroups)}")
			items = [tuple2item(ig) for ig in self.igroups[idx]]
			items = self.propagate(items)
			follows = self.build_follow(items)
			self.igroups[idx] += self.combine_ahead(
				items, follows)
			self.igroups[idx] = sorted(list(set(self.igroups[idx])))
			if self.find_collision(idx):
				continue
			#for ig in self.igroups[idx]:
			#	print(idx, tuple2item(ig))
			self.forward(self.igroups[idx])
			glen = len(self.igroups[idx])
			idx += 1
		return self.build2()
