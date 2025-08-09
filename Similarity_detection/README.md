\# Code Embedding and Similarity Detection



This folder contains resources and scripts for generating embeddings and evaluating similarity between decompiled code and a function library using `GraphCodeBERT`.



\## Folder Structure



\- \*\*1\_original\_csv\_fine\_grain\*\*: Contains the final output of decompiled functions in CSV format.

\- \*\*3\_embedding\_npy\_fine\_grain\*\*: Stores the embeddings of the decompiled functions generated using `GraphCodeBERT` in `.npy` format.

\- \*\*function\_library\_embeddings.npy\*\*: The embeddings of source code functions, stored in `.npy` format, generated using `GraphCodeBERT`.

\- \*\*1-direct\_code\_embedding.py\*\*: Python script for generating embeddings for decompiled code using `GraphCodeBERT` and storing them as `.npy` files.

\- \*\*2-detection.py\*\*: Python script for detecting similarity between decompiled code and a function library. It outputs the top-1, top-3, and top-5 similarity scores.



\## Overview



This setup is designed to generate embeddings for decompiled code using `GraphCodeBERT` and compute the similarity between the decompiled code and a function library.



\- The \*\*embedding generation process\*\* is handled by `1-direct_code_embedding.py`, which processes decompiled code and stores the embeddings in `.npy` format.

\- The \*\*detection process\*\* is handled by `2-detection.py`, which compares the decompiled code embeddings against a pre-generated function library (`function_library_embeddings.npy`) and outputs the top-1, top-3, and top-5 similarity results.



\## Usage



To generate embeddings for decompiled code:

```bash

python 1-direct_code_embedding.py 



To detect similarity between the decompiled code and the function library:

python 2-detection.py 





