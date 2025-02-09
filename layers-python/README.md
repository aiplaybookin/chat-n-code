# Steps to create layers

### Create a file will all required packages
vi requirements.txt

### Create a virtual env
python3.12 -m venv create_layer

### Activate the virtual env
source create_layer/bin/activate

### Install all libraries
pip install -r requirements.txt

>> This uses venv to create a Python virtual environment named create_layer. It then installs all required dependencies in the create_layer/lib/python3.12/site-packages directory.

### Create a folder in accordance with Lamdba layers
mkdir python

### Copy contents 
cp -r create_layer/lib python/

### zip the folder 
zip -r layer_content.zip python