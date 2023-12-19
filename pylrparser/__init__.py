import math
from importer import importer
importer("../../pyltr/pyltr", __file__)

def align_output(parsed, orig, names):
	orig_idx = 0
	def align_output_recurse(parsed):
		nonlocal orig_idx
		if isinstance(parsed, str):
			orig_idx += 1
			return orig[orig_idx - 1]
		new_body = [names[parsed[0]]]
		for body in parsed[1:]:
			new_body.append(align_output_recurse(body))
		return new_body
	return align_output_recurse(parsed)
