import pyltr

def load_rules(s):
	s = pyltr.striphash(s)
	rules = pyltr.parse_slit(s)
	assert(rules[0][0] == "S")

	toksym = set("$")
	rulesym = set()
	def imap(s):
		rulesym.add(s)
		return s
	def smap(s):
		s = s.s
		toksym.add(s)
		return s
	rulesym.add("S")
	names = []
	rules2 = []
	for rule_group in rules:
		start = rule_group[0]
		for generation in rule_group[1:]:
			names.append(generation[0])
			mapped = pyltr.ltr_map(generation[1:], imap, smap)
			rules2.append((start, mapped))
	return list(toksym), list(rulesym), rules2, names
