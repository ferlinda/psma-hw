import networkx as nx
import csv
from itertools import zip_longest
import random
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn import metrics

from csv import writer
from csv import reader

def add_column_in_csv(input_file, output_file, transform_row):
    """ Append a column in existing csv using csv.reader / csv.writer classes"""
    # Open the input_file in read mode and output_file in write mode
    with open(input_file, 'r') as read_obj, \
            open(output_file, 'w', newline='') as write_obj:
        # Create a csv.reader object from the input file object
        csv_reader = reader(read_obj)
        # Create a csv.writer object from the output file object
        csv_writer = writer(write_obj)
        # Read each row of the input csv file as list
        for row in csv_reader:
            # Pass the list / row in the transform function to add column text for this row
            transform_row(row, csv_reader.line_num)
            # Write the updated row / list to the output file
            csv_writer.writerow(row)

G = nx.Graph()
r = csv.reader(open('data_train_edge_noheader.csv','r'))
edges = []
for edge in r: 
	edges.append((int(edge[0]), int(edge[1])))

connected_pair=[]
for pair in edges:
    if edges.count((pair[1],pair[0]))!=0 and pair[1]!=pair[0]:
        connected_pair.append(pair)

G.add_edges_from(connected_pair)
all_nodes=list(G.nodes)

r = csv.reader(open('data_train_edge_noheader.csv','r'))
edges = dict()
for edge in r:
	edges[(edge[0], edge[1])] = 1
    
missing_edges = set([])
while (len(missing_edges)<5673):
	a=random.choice(all_nodes)
	b=random.choice(all_nodes)
	tmp = edges.get((a,b),-1)
	if tmp == -1 and a!=b:
		try:
			if nx.shortest_path_length(G,source=a,target=b) > 2: 

				missing_edges.add((a,b))
			else:
				continue  
		except:  
				missing_edges.add((a,b))              
	else:
		continue

missing_edges=list(missing_edges)

edge_list_res=[]
temp_list=[]
for edge in G.edges:
    temp_list=list(edge)
    temp_list.append(1)
    edge_list_res.append(tuple(temp_list))

temp_list=[]
for edge in missing_edges:
    temp_list=list(edge)
    temp_list.append(0)
    edge_list_res.append(tuple(temp_list))

edge_list_res=list(set(edge_list_res))
with open('temp_csv.csv', 'w') as f: 
    write = csv.writer(f)  
    write.writerows(edge_list_res) 

r = csv.reader(open('temp_csv.csv','r'))
edges = []
for edge in r: 
	edges.append((int(edge[0]), int(edge[1])))

jc_list=[]
for i in list(nx.jaccard_coefficient(G, ebunch=edges)): 
    jc_list.append(i[2])

aa_list=[]
for i in list(nx.adamic_adar_index(G, ebunch=edges)): 
    aa_list.append(i[2])

pa_list=[]
for i in list(nx.preferential_attachment(G, ebunch=edges)): 
    pa_list.append(i[2])

rai_list=[]
for i in list(nx.resource_allocation_index(G, ebunch=edges)): 
    rai_list.append(i[2])

add_column_in_csv('temp_csv.csv', 'temp_csv_2.csv', lambda row, line_num: row.append(jc_list[line_num - 1]))
add_column_in_csv('temp_csv_2.csv', 'temp_csv.csv', lambda row, line_num: row.append(aa_list[line_num - 1]))
add_column_in_csv('temp_csv.csv', 'temp_csv_2.csv', lambda row, line_num: row.append(pa_list[line_num - 1]))
add_column_in_csv('temp_csv_2.csv', 'temp_csv.csv', lambda row, line_num: row.append(rai_list[line_num - 1]))

df = pd.read_csv("temp_csv.csv", header=None)
df.to_csv("temp_csv.csv", header=["node1", "node2", "ans", "jc", "aa", "pa", "rai"], index=False)
df = pd.read_csv("temp_csv.csv")

print(df.head())

y = df[['ans']]
X = df[['jc', 'aa', 'pa', 'rai']]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

clf=RandomForestClassifier(n_estimators=100)

clf.fit(X_train,y_train)

y_pred=clf.predict(X_test)

print("Accuracy:",metrics.accuracy_score(y_test, y_pred))

r2 = csv.reader(open('predict_noheader.csv','r'))
missing_index=[]
edges_predict = []
edges_predict_norm=[]
id_list=[]
count=0
for edge in r2: 
    edges_predict_norm.append((int(edge[0]), int(edge[1])))
    id_list.append(count)
    if (G.has_node(int(edge[0])) and G.has_node(int(edge[1]))) and int(edge[0])!=int(edge[1]):
	    edges_predict.append((int(edge[0]), int(edge[1])))
    else:
        missing_index.append(count)
    count+=1

jc_list=[]
for i in list(nx.jaccard_coefficient(G, ebunch=edges_predict)): 
    jc_list.append(i[2])

aa_list=[]
for i in list(nx.adamic_adar_index(G, ebunch=edges_predict)): 
    aa_list.append(i[2])

pa_list=[]
for i in list(nx.preferential_attachment(G, ebunch=edges_predict)): 
    pa_list.append(i[2])

rai_list=[]
for i in list(nx.resource_allocation_index(G, ebunch=edges_predict)): 
    rai_list.append(i[2])

node1_list=[]
node2_list=[]
for edge in edges_predict:
    node1_list.append(edge[0])
    node2_list.append(edge[1])

d = [node1_list, node2_list]
export_data = zip_longest(*d, fillvalue = '')
with open('temp_csv_predict2.csv', 'w', encoding="ISO-8859-1", newline='') as myfile:
      wr = csv.writer(myfile)
      wr.writerows(export_data)
myfile.close()

add_column_in_csv('temp_csv_predict2.csv', 'temp_csv_predict2_2.csv', lambda row, line_num: row.append(jc_list[line_num - 1]))
add_column_in_csv('temp_csv_predict2_2.csv', 'temp_csv_predict2.csv', lambda row, line_num: row.append(aa_list[line_num - 1]))
add_column_in_csv('temp_csv_predict2.csv', 'temp_csv_predict2_2.csv', lambda row, line_num: row.append(pa_list[line_num - 1]))
add_column_in_csv('temp_csv_predict2_2.csv', 'temp_csv_predict2.csv', lambda row, line_num: row.append(rai_list[line_num - 1]))

df_predict = pd.read_csv("temp_csv_predict2.csv", header=None)
df_predict.to_csv("temp_csv_predict2.csv", header=["node1", "node2", "jc", "aa", "pa", "rai"], index=False)
df_predict = pd.read_csv("temp_csv_predict2.csv")

X = df_predict[['jc', 'aa', 'pa', 'rai']]

y_pred=clf.predict(X)

y_pred_temp=[]
y_pred_temp=list(y_pred)

for i in missing_index:
    y_pred_temp.insert(i,0)


d = [id_list, y_pred_temp]
export_data = zip_longest(*d, fillvalue = '')
with open('ans_2.csv', 'w', encoding="ISO-8859-1", newline='') as myfile:
      wr = csv.writer(myfile)
      wr.writerow(("predict_nodepair_id", "ans"))
      wr.writerows(export_data)
myfile.close()
