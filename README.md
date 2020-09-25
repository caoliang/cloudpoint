1. Install Open3d

conda install -c open3d-admin open3d


2. Install pillow

conda install -c anaconda pillow

3. Build Open3d

mkdir build
cd build
cmake -DBUILD_CUDA_MODULE=ON -G "Visual Studio 14 2015 Win64" .. 

cmake --build . --parallel %NUMBER_OF_PROCESSORS% --config Release --target ALL_BUILD

cmake --build . --parallel %NUMBER_OF_PROCESSORS% --config Release --target python-package

cmake --build . --parallel %NUMBER_OF_PROCESSORS% --config Release --target pip-package

cmake --build . --parallel %NUMBER_OF_PROCESSORS% --config Release --target conda-package

cmake --build . --parallel %NUMBER_OF_PROCESSORS% --config Release --target install-pip-package

4. Install Vedo

conda install -c conda-forge vedo

5. Install tqdm

conda install -c conda-forge tqdm