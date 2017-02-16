import sys,os

name_folder = sys.argv[1]

dev_amr = '(p / possible-01 :polarity - :ARG1 (e / ensure-01 :ARG0 (y / you) :ARG1 (a / and :op1 (u / upset-01 :ARG1 y :degree (r / really)) :op2 (w / want-01 :polarity - :ARG0 y :ARG1 (h / hit-01 :ARG0 (t / they) :ARG1 (p2 / person :ARG0-of (h2 / have-rel-role-91 :ARG1 y :ARG2 (k / kid))) :time (e2 / ever) :mod (a2 / again))))) :ARG1-of (c / cause-01 :ARG0 (a3 / amr-unknown)))\n'
test_amr = '(c / close-01 :ARG1 (i / investigate-01 :ARG1 (a / activity-06 :ARG0 (c2 / country :wiki "Iran" :name (n3 / name :op1 "Iran")) :mod (n2 / nucleus))) :time (n / now))\n'

ulf_amr = '(s / state-01 :ARG0 (p / person :ARG0-of (h / have-org-role-91 :ARG1 (c / country :name (n / name)) :ARG2 president) :name (n2 / name)) :ARG1 (a / and :op1 (w / want-01 :ARG0 (p2 / person) :ARG1 (d / do-02 :ARG0 p2)) :op2 (p3 / person :mod (c2 / country :name (n3 / name)))) :time (d2 / date-entity :year 2007))\n'

for root, dirs, files in os.walk(name_folder):
	for f in files:
		if f.endswith('.tf') and 'all' not in f and 'ids' not in f:
			f_path = os.path.join(root, f)
			num_lines = sum(1 for line in open(f_path))
			new_path = f_path.split('working/')[1]
			print new_path
			if 'dev' in new_path:
				with open(new_path,'w') as fp:
					fp.write(ulf_amr * num_lines)
				fp.close()	
			
			elif 'test' in new_path:
				with open(new_path,'w') as fp:
					fp.write(ulf_amr * num_lines)
							
