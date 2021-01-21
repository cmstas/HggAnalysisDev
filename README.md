# HggAnalysisDev
Repository for developing H->gg analyses, starting from (skimmed) nanoAOD inputs.
Will contain machinery for the standard tasks in developing an H->gg analysis:
* Looping over nanoAOD and making yield tables + data/MC plots
* MVA training: MVA input file prep, tools for BDT/DNN training, writing output to an ntuple
* Signal region optimization: optimize cut(s) on MVA(s) to maximize expected sensitivity to some observable
