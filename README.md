# CTC-Quant
CTC-Quant is an application customised to quantify CTC subtypes including epithelial (epCTCs), biphenotypic (bipCTCs) and mesenchymal (mCTCs). mCTC clusters are also identified and quantified. In brief, fluorescent microscope images of CTCs isolated using a size-filtration microsieve technology are classified based on their fluorescent staining patterns. CTCs are further differentiated from background cells based on their staining intensities. mCTC clusters are identified as cell segments with > 2 cells in a close periphery. A detailed description of CTC-Quant’s algorithmic pipeline is described in a study of lung, breast and nasopharyngeal cancer samples: “”. 

**To set up a virtual environment in Conda:** \
  conda create -n ctcquant-env python=3.6 \
  conda install -n ctcquant-env pandas=1.1.3 \
  conda install -n ctcquant-env numpy=1.19.2 \
  conda install -n ctcquant-env scipy=1.5.2 \
  conda install -n ctcquant-env -c free scikit-image=0.17.2 \
  conda install -n ctcquant-env -c free scikit-learn=0.23.2 \
  conda install -n ctcquant-env matplotlib=3.3 \
  conda install -n ctcquant-env pickle5 \
  conda install -n ctcquant-env pyqt

**To activate the environment:** \
  conda activate ctcquant-env
  
**Navigate to source code directory:** \
  cd (path to source code) eg. C:/Users/limsh/Desktop/code/source
  
**Launch exe:** \
  python mygui_run.py
  
**To deactivate the environment:** \
  conda deactivate
