import os
import datetime
import os.path
import shutil
import sys
ndcg = {}
Map = {}
result = [0]*12

def ifNotExistMk(path):
	"""
		check if the fold exists ,if not make it
	"""
	if not os.path.exists(path):
		os.makedirs(path)

def getLastTime(basePath,datasetname):
	path = os.path.join(basePath,"saved_model",datasetname)
	
	ifNotExistMk(path)

	folds = []
	for i in os.listdir(path):
		if os.path.isdir(os.path.join(path,i)):
			folds.append(i)
	if len(folds) > 0:
		return reduce(lambda a,b: a if a >b else b,folds,folds[0])
	return ""
def getModelTime(basepath,datasetname):
	path = os.path.join(basepath,"data",datasetname,"model")
	date = datetime.datetime.fromtimestamp(os.path.getmtime(path))
	return date.strftime("%Y%m%d%H%M%S")

def isUpdate(basepath,datasetname):
	t1 = getModelTime(basepath,datasetname)
	t2 = getLastTime(basepath,datasetname)
	if t1 > t2:
		return True 
	return False 

def backup(basepath,datasetname):
	name = getModelTime(basepath,datasetname)
	path = os.path.join(basepath,"saved_model",datasetname,name)

	for f in ('data','eval'):
		src = os.path.join(basepath,f,datasetname)
		t = os.path.join(path,f)
		shutil.copytree(src,t)

def average():
	global ndcg,Map,result
	test = ndcg["testing"]
	sum = [0.0]*12
	for tmp in test:
		for i in range(0,len(tmp)):
			sum[i] += tmp[i]
	for tmp in Map["testing"]:
		sum[11] += tmp
	for i in range(0,12):
		result[i] = sum[i]/5.0

def check(a,b,c):
	assert(a == "performance")
	assert(b == "on")
	assert(c == "set")

def doLine(line,lineNum):
	global vali_measure,dataset,algorithm,cur_subset,Map,ndcg
	if lineNum == 1:
		_,vali_measure = map(lambda x: x.strip().lower(),line.split(":"))
	elif lineNum == 2:
		_,dataset = map(lambda x: x.strip().lower(),line.split(":"))
	elif lineNum == 3:
		_,algorithm = map(lambda x: x.strip(),line.split(":"))
	elif lineNum == 4 or lineNum == 17 or lineNum == 30 :
		a,b,cur_subset,c = map(lambda x: x.strip().lower(),line.split(" "))
		check(a,b,c)
		if cur_subset.startswith("test"):
			cur_subset = "testing"
		elif cur_subset.startswith("train"):
			cur_subset = "training"
		elif cur_subset.startswith("vali"):
			cur_subset = "validation"
		else:
			sys.exit(-1)

	elif (lineNum > 5 and lineNum < 11) or \
				(lineNum > 18 and lineNum < 24) or \
				(lineNum > 31 and lineNum < 37):
		line = line.strip("\t")
		x = map(lambda x: x.strip(),line.split("\t"))[1:]
		assert(len(x) == 11)
		x = map(float,x)

		if ndcg.has_key(cur_subset):
			ndcg[cur_subset].append(x)
		else:
			ndcg[cur_subset] = []
			ndcg[cur_subset].append(x)
	elif (lineNum > 11 and lineNum < 17) or \
				(lineNum > 24 and lineNum < 30) or \
				(lineNum > 37 and lineNum < 43):
		line = line.strip("\t")
		x = map(lambda x: x.strip(),line.split("\t"))[11]
		x = float(x)
		if Map.has_key(cur_subset):
			Map[cur_subset].append(x)
		else:
			Map[cur_subset] = []
			Map[cur_subset].append(x)
	elif lineNum < 43:
		return
	else:
		sys.exit(-1)

def readFile(fileName):
	global ndcg, Map, result
	ndcg = {}
	Map = {}
	result = [0]*12
	lineNum = 1
	with open(fileName) as fin:
		for line in fin:
			line = line.strip("\n")
			if line == "":
				continue
			doLine(line,lineNum)
			lineNum += 1
	average()


def save(filename,timestr,modeltime):
	global result
	flag = False
	if not os.path.exists(filename):
		flag = True
	with open(filename,'a') as fout:
		if flag :
			fout.write("time\tmodel_time\tNDCG@1\tNDCG@2\tNDCG@3\tNDCG@4\tNDCG@5\t"+\
				"NDCG@6\tNDCG@7\tNDCG@8\tNDCG@9\tNDCG@10\tMeanNDCG\tMap\n")
			flag = False
		fout.write("%s\t%s\t"%(timestr,modeltime))
		for tmp in result:
			fout.write("%.4f\t"%tmp)
		fout.write("\n")

def lastLineTime(filename):
	if  not os.path.exists(filename):
		return ""
	f = open(filename)
	t = f.readlines()
	time = t[len(t)-1].split()[0]
	f.close()
	return time 

def addRecord(basepath,datasetname):
	path = os.path.join(basepath,"eval",datasetname)
	dstPath = os.path.join(basepath,"saved_model",datasetname)
	for i in os.listdir(path):
		date = datetime.datetime.fromtimestamp(os.path.getmtime(os.path.join(path,i)))
		timestr = date.strftime("%Y%m%d%H%M%S")		
		if "MAP" in i:
			t1 = lastLineTime(os.path.join(dstPath,"msr_map"))
			if timestr > t1:
				readFile(os.path.join(path,i))
				modeltime = getModelTime(basepath,datasetname)
				save(os.path.join(dstPath,"msr_map"),timestr,modeltime)
		elif "NDCG" in i:
			t1 = lastLineTime(os.path.join(dstPath,"msr_ndcg"))
			if timestr > t1:
				readFile(os.path.join(path,i))
				modeltime = getModelTime(basepath,datasetname)
				save(os.path.join(dstPath,"msr_ndcg"),timestr,modeltime)

def getFile(dir):
	files = []
	dir = os.path.abspath(dir)	
	for i in os.listdir(dir):
		files.append(os.path.join(dir,i))
	return files

def run(baselines):
	#algorithms = getFile(baselines)
	algorithms = []
	#print baselines
	for i in os.listdir(baselines):
			if os.path.isdir(os.path.join(baselines,i)):
				algorithms.append(os.path.join(baselines,i))
	for algorithm in algorithms:
		datasets = []
		for i in os.listdir(os.path.join(algorithm,"eval")):
			if os.path.isdir(os.path.join(algorithm,"eval",i)):
				datasets.append(i)
		for dataset in datasets:
			if isUpdate(algorithm,dataset):
				backup(algorithm,dataset)
				addRecord(algorithm,dataset)


if __name__ =='__main__':
	run(sys.argv[1])
#	shutil.copytree("./result","abc")