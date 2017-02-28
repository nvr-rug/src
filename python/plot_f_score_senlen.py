import json,sys
import matplotlib
# Force matplotlib to not use any Xwindows backend.
matplotlib.use('Agg')
import matplotlib.pyplot as plt

json_data1 = open(sys.argv[1])
json_data2 = open(sys.argv[2])
json_data3 = open(sys.argv[3])
json_data4 = open(sys.argv[4])
json_data5 = open(sys.argv[5])
json_data6 = open(sys.argv[6])

f1_scores_seq = json.load(json_data1)
max_lengths_seq = json.load(json_data2)
num_sents_seq = json.load(json_data3)

f1_scores_camr = json.load(json_data4)
max_lengths_camr = json.load(json_data5)
num_sents_camr = json.load(json_data6)

for idx in range(0, len(f1_scores_camr)):
	f1_scores_camr[idx] -= 0.0025
	f1_scores_seq[idx] -= 0.0025

def do_event_plot(plot1,plot2, plot3, plot4,jpg):
	plt.figure(1)
	#plt.plot(plot1,plot2, 'k-->',lw=1,markevery = 3)
	#plt.plot(plot3, plot4, 'k-o', lw=1, markevery = 3)
	
	plt.plot(plot1,plot2, 'k--',lw=1, label = "seq-to-seq model")
	plt.plot(plot3, plot4,'k', lw=1, label =  "CAMR ensemble")
	
	plt.xlabel('Maximum sentence length (words)',size=15)
	plt.ylabel('F-score',size=16)
	plt.xticks([0,5,10,15,20,25,30,35,40,45,50], fontsize = 14)
	plt.yticks([0.40,0.50,0.60,0.70,0.80,0.90, 1.0], fontsize = 14)
	plt.legend(loc=(0.5,0.6), shadow=True)
	#plt.text(150,0.67 , str(num_events[153] -1),fontweight='bold')
	
	plt.savefig(jpg)
		
do_event_plot(max_lengths_seq, f1_scores_seq, max_lengths_camr, f1_scores_camr, 'plot_max_length.png')
