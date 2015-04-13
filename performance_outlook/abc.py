import sys
import os 
import shutil 


def cp(src,dst):
	if os.path.isfile(src): 
		open(dst, "wb").write(open(src, "rb").read())


def getBaselines(rootPath):
	files = []
	rootPath = os.path.abspath(rootPath)
	for i in os.listdir(rootPath):
		files.append(os.path.join(rootPath,i))
	return files

def cpOneFold(path,dst):
	if not os.path.isdir(path):
		return 
	for i in os.listdir(path):
		cp(os.path.join(path,i),os.path.join(dst,i))

def run(rootPath,dstPath):
	paths = getBaselines(rootPath)
	for path in paths:
		evalPath = os.path.join(path,'eval')
		for folds in os.listdir(evalPath):
			cpOneFold(os.path.join(evalPath,folds),dstPath)

if __name__ == '__main__':
	if len(sys.argv) < 2:
		sys.exit(-1)
	#argv1:baselines directory
	output_pth = 'output'#os.path.join(sys.argv[1],'performance_outlook','output')
	#print output_pth
	baselines_pth = os.path.join(sys.argv[1],'baselines')
	input_pth = 'input'#os.path.join(sys.argv[1],'performance_outlook','input')
	#print input_pth
	if os.path.isdir(output_pth):
		#print 'remove output_pth'
		os.system('rm -rf %s'%output_pth)
	if  os.path.exists(input_pth):
		#print 'remove input_pth'
		os.system('rm -rf %s'%input_pth)
	os.system('mkdir %s'%input_pth);	
	run(baselines_pth,input_pth)
	result_pth = os.path.join(sys.argv[1],'performance_outlook','result.py');
	os.system("python %s %s %s"%(result_pth,input_pth,output_pth))