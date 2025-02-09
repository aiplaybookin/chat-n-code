# Steps to create layers

### Create a file will all required packages
```
vi requirements.txt
```
### Create a virtual env (based on your python version)
```python3.12 -m venv create_layer```

### Activate the virtual env
```source create_layer/bin/activate```

### Install all libraries
```pip install -r requirements.txt```


This uses venv to create a Python virtual environment named create_layer. It then installs all required dependencies in the create_layer/lib/python3.12/site-packages directory.

### Create a folder to be in accordance with Lamdba layers folder structure
```mkdir python```

### Copy contents 
```cp -r create_layer/lib python/```

### zip the folder 
```zip -r layer_content.zip python```

### Now create a layer in AWS Lambda and upload the zip file