\# Decompiled code Recovery



This folder contains resources and scripts for the decompiled code  recovery process of code using different phases and configurations.



\## Folder Structure



\- \*\*Phase1\_Decompiled\_code\_with\_guidance\*\*: Contains examples provided by the first phase of semantic recovery.

\- \*\*Phase2\_Decompiled\_code\_with\_CFS\*\*: Contains examples provided by the second phase of control flow recovery.

\- \*\*Phase3\_Decompiled\_code\_for\_final\_recovery\*\*: Contains examples provided by the third phase of final recovery.

\- \*\*DeepSeek\_config.ini\*\*: Configuration file for the LLM.

\- \*\*document\_processor.py\*\*: Script for processing documents.

\- \*\*Phase1\_Recover\_with\_Guidance.py\*\*: Script for the first phase of semantic recovery.

\- \*\*Phase2\_Recover\_with\_CFS.py\*\*: Script for the second phase of control flow recovery.

\- \*\*Phase3\_Final\_Recovery.py\*\*: Script for the third phase of final recovery.

\- \*\*prompt\_templates.py\*\*: Script containing Prompt templates.



\## Overview



This setup is designed to handle the decompilation and recovery of code through multiple phases using specified scripts and configurations.



\- The \*\*semantic recovery process\*\* is handled by `Phase1\_Recover\_with\_Guidance.py`, which provides examples in `Phase1\_Decompiled\_code\_with\_guidance`.

\- The \*\*control flow recovery process\*\* is handled by `Phase2\_Recover\_with\_CFS.py`, which provides examples in `Phase2\_Decompiled\_code\_with\_CFS`.

\- The \*\*final recovery process\*\* is handled by `Phase3\_Final\_Recovery.py`, which provides examples in `Phase3\_Decompiled\_code\_for\_final\_recovery`.

\- The \*\*LLM configuration\*\* is managed by `DeepSeek\_config.ini`.

\- The \*\*prompt templates\*\* are stored in `prompt\_templates.py`.



\## Usage



To perform semantic recovery (Phase 1):



```bash

python Phase1\_Recover\_with\_Guidance.py

```



To perform control flow recovery (Phase 2):



```bash

python Phase2\_Recover\_with\_CFS.py

```



To perform final recovery (Phase 3):



```bash

python Phase3\_Final\_Recovery.py

```



</xaiArtifact>

