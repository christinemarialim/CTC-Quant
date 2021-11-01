# CTC-Quant
CTC-Quant is an application customised to quantify CTC subtypes including epithelial (epCTCs), biphenotypic (bipCTCs) and mesenchymal (mCTCs). mCTC clusters are also identified and quantified. In brief, fluorescent microscope images of CTCs isolated using a size-filtration microsieve technology are classified based on their fluorescent staining patterns. CTCs are further differentiated from background cells based on their staining intensities. mCTC clusters are identified as cell segments with > 2 cells in a close periphery. A detailed description of CTC-Quant’s algorithmic pipeline is described in a study of lung, breast and nasopharyngeal cancer samples: “”. 

**To create a virtual environment in Conda:** \
  conda create -n ctcquant-env python=3.6
  
**To activate the environment:** \
  conda activate ctcquant-env

**To install required packages:** \
  pip install pyqt5 \
  pip install numpy==1.16 \
  pip install matplotlib==3.3.4 \
  pip install pandas==1.1.3 \
  pip install scipy==1.5.2 \
  pip install scikit-image==0.17.2 \
  pip install scikit-learn==0.23.2
  
**Navigate to source code directory:** \
  cd (path to source code) eg. C:/Users/limsh/Desktop/code/source
  
**Launch exe:** \
  python mygui_run.py
  
**To deactivate the environment:** \
  conda deactivate
