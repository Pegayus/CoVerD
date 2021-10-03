# CoVerD: Community-based Vertex Defense against Crawling Adversaries
This is the code for our ppaer, to appear in the proceedings of Complex Networks 2021.

## Scripts under ```src```:
* ```data_preprocessing.py```: Run this script seperately from the rest of the repo to prepare the dataset used by ```main.py```.
* ```coverd.py```: The code for our algorithm, coverd. This script if used by ```main.py```.
* ```attacker.py```: The local and global perturbation baselines that we have used in the paper to benchmark coverd. This script is used by ```main.py```.
* ```utils.py```: The helper functions used througout the repository.
* ```main.py```: The main script that invokes all the processing done by the modules above. To reproduce our experiments, you have to run this script as explained below.

## Sample usage:
### Defense mode 
```
python main.py --mode defense --defend coverd roam nothing --name lastfm 
```
### Attack mode
```
python main.py --mode attack --attack bfs dfs --name lastfm 
```

