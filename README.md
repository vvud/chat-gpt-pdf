# ChatGPT PDF
This API use to lookup and answer question from a owner-manual pdf

## Step 1: Install requirements packages

Your will need `python` to run the API

1. Run `python -m venv ./venv` to create virtual environment
2. Access virtual environment `source venv/bin/activate`
3. Install dependencies packages `pip install -r requirements.txt`
4. ENVs templates `.env` clone from `.env.template`

## Step 2: Run the api packages

1. In order to run the API you will need PDF's database first
   
   Run `python ingest.py` to create vector model.
   
   To config: go to __main function in `ingest.py` file

2. Then, run `python app.py` to start the API

