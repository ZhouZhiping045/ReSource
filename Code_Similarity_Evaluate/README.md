\# Code Similarity Detection and Evaluation



This folder contains the resources and scripts for evaluating the similarity between source code and optimized/decompiled code. It includes the original source code, optimized decompiled code, and the script used to calculate similarity.



\## Folder Structure



\- \*\*0-sourcecode\*\*: Contains the original source code files for the evaluated programs.

\- \*\*fine\_grain\_final\_output2txt\*\*: Stores the optimized decompiled code files.

\- \*\*similarity.py\*\*: A Python script used for calculating code similarity between the original source code and the decompiled code.



\## Overview



This setup is designed to evaluate the structural and semantic similarity between two sets of code: the original source code and the decompiled code after optimizations and obfuscation transformations. The `similarity.py` script computes different similarity metrics, such as interface similarity, structural similarity, control flow similarity, Halstead similarity, and token-editing similarity, to assess how closely the decompiled code matches the original source code.



\## Usage



To evaluate the similarity, run the `similarity.py` script. The script requires the original source code and the corresponding decompiled code as input and will output the similarity scores based on several metrics.



Example command:

```bash

python similarity.py --source 0-sourcecode --decompiled fine\_grain\_final\_output2txt



