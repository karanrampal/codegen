# Code generation
Convert natural language text into SQL code which can be validated and executed in BigQuery.

I use google gemini-1.5-pro model to convert text to SQL code and then check for some formatiing error using regular expressions. Once the generated query is checked it can be executed in Bigquery.

Streamlit is used for implementing the UI.

## Install
To install the libraries, create the virtual environment. I use conda but venv or any other is also fine. For conda, from project root dir, do the following,

`make install` or if `make` is not installed then run,
```
conda env create -f environment.yml
conda activate gen-env
```

Else create environement using venv etc. and run,

`make install_ci` or if `make` is not installed then run `pip install -r requirements.txt`

 ### Notes:
  - For venv run the following commands to install an virtual env.,
  ```
  python -m venv ./.venv
  source ./.venv/bin/activate

  ```
  - All above installation commands assumed `python 3.10`, if using other version of python then change src files accordingly.
## Useage
First authenticate to your GCP project by running, (assumes that you have configured gcloud i.e. ran `gcloud init` beforehand)

`gcloud auth login`

Ten to run the Gradio server locally run the following command from project root directory

`streamlit run ./src/Home.py`

This assumes that you have run `chmod +x main.py`. Else run,

`python -m streamlit run ./src/Home.py`

## Deploy
To deploy to cloud run first make sure you are authenticated into gcp,

`gcloud auth login`

Then build the image and push to artifact registry using (this assumes you have set up the artifact registry and made necessary changes into the makefile),

`make docker_bp`

Next run the following command to deploy on cloud run,

`gcloud run deploy <service_name> --image <image_name>`
