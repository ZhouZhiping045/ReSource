<xaiArtifact artifact_id="ab3b9917-ef94-40bb-baa9-36110b1edac5" artifact_version_id="5163e9a9-cf29-4da7-a6d3-30d3a5b7af22" title="README.md" contentType="text/markdown">

# Code Recovery and Similarity Detection Framework

This repository provides a set of tools for recovering decompiled code, predicting control flow, and evaluating code similarity. The tools are organized into several modules that handle different stages of the recovery process and similarity detection.

## Folder Structure

### 1. **construct_semantic_database**

&nbsp;  - This module is designed to build the **Semantic Distortion Database**, which contains common decompiler artifacts and corresponding recovery suggestions. Currently, this feature is not yet available.

&nbsp;  - **Purpose**: To predict and guide semantic recovery using the database.

### 2. **control_flow_predict**

&nbsp;  - This module is used for **control flow prediction**, which helps in recovering control structures like loops and conditionals that may have been flattened or altered during optimization or obfuscation. This functionality is also not yet provided.

&nbsp;  - **Purpose**: To predict control flow sequences for decompiled code.

### 3. **Decompiled_code_recovery**

&nbsp;  - This module contains the **three-stage recovery pipeline**, which optimizes and recovers decompiled code by:

&nbsp;    1. **Semantic recovery**: Restoring program behavior using context-aware semantic adjustments.
&nbsp;    2. **Structural recovery**: Rebuilding control flow and refining code layout for improved coherence.
&nbsp;    3. **Lexical recovery**: Enhancing variable names and code structure for better readability.

&nbsp;  - **Purpose**: To transform decompiled code into a source-like format that maintains functionality and enhances readability.

### 4. **Similarity_detection**

&nbsp;  - This module is responsible for **similarity detection** between decompiled functions and a pre-built function library. It uses embedding models (e.g., `GraphCodeBERT`) to compute the similarity between functions.

&nbsp;  - **Purpose**: To detect functional similarities between the recovered code and functions in a library using embeddings.

### 5. **Code_Similarity_Evaluate**

&nbsp;  - This module is used to **evaluate code similarity**. It takes in the decompiled and recovered code and evaluates its similarity to the source code or library based on various similarity metrics such as token-level similarity, structural similarity, and semantic alignment.

&nbsp;  - **Purpose**: To assess the effectiveness of the recovery process and the similarity between decompiled and source code.

### 6. **requirements.txt**

&nbsp;  - This file lists the required dependencies and libraries needed to run the scripts and modules in this repository. You can install the dependencies with:

&nbsp;    
    pip install -r requirements.txt
   

## Usage

Once the relevant modules are available, you can use them in the following manner:

1. **Semantic Database Construction & Prediction**:  
&nbsp;  Use the `construct_semantic_database` module to generate and predict semantic recovery suggestions for decompiled code.

2. **Control Flow Prediction**:  
&nbsp;  Use the `control_flow_predict` module to predict the control flow structures for the decompiled code.

3. **Decompiled Code Recovery**:  
&nbsp;  Use the `Decompiled_code_recovery` module to recover decompiled functions by optimizing their lexical, semantic, and structural aspects.

4. **Similarity Detection**:  
&nbsp;  Use the `Similarity_detection` module to compute function similarity using embeddings.

5. **Code Similarity Evaluation**:  
&nbsp;  Use the `Code_Similarity_Evaluate` module to evaluate how well the recovered code matches the source or function library.

## Future Updates

- **construct_semantic_database** and **control_flow_predict** modules are currently under development. These modules will be available after the paper is accepted and the repository is updated.

</xaiArtifact>

