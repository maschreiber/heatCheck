import os
import csv
shots = []

with open('grayson_shot.csv') as fin:
	data_in = csv.DictReader(fin)
	for shot in data_in:
		shots.append({'x': int(shot['x']), 'y': int(shot['y']), 'made': int(shot['made'])})
		
fin.close()
print(shots)