# CoVerD: Community-based Vertex Defense against Crawling Adversaries
This is the code for our ppaer ```CoVerD```, to appear in the proceedings of Complex Networks 2021.

## Scripts under ```src```:
* ```data_preprocessing.py```: Run this script seperately from the rest of the repo to prepare the dataset used by ```main.py```.
* ```coverd.py```: The code for our algorithm, coverd. This script if used by ```main.py```.
* ```attacker.py```: The local and global perturbation baselines that we have used in the paper to benchmark coverd. This script is used by ```main.py```.
* ```utils.py```: The helper functions used througout the repository.
* ```main.py```: The main script that invokes all the processing done by the modules above. To reproduce our experiments, you have to run this script as explained below.

## Data
* ```data/raw```: All the dataset are available from SNAP repository. The original datasets are processed using ```data_preprocessing.py``` into pickled files. This data will later be used to run a defender and/or attacker on.
* ```data/defended```: The defended graphs after running all our defender baselines on the raw datasets. Only ```lastfm``` data is included in this repository as a sample. The other datasets can be generated by running ```main.py``` on corresponding data under ```data/raw```.

## Results
A sample result of our experiments in the paper for the ```lastfm``` dataset is included under ```results``` directory. 

## Sample usage:
### Defense mode 
```
python main.py --mode defense --defend coverd roam nothing --name lastfm 
```
### Attack mode
```
python main.py --mode attack --attack bfs dfs --name lastfm 
```

