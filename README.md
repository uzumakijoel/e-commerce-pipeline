**E-Commerce Data Pipeline**

Overview

This project implements an end-to-end data pipeline that extracts data from a REST API, transforms and prepares it using python and pandas, and loads the processed data into a MYSQL database.
This project demontrates pratical skills in API integration, data transformation, database connectivity, pipeline organization, logging and error handling.

Objectives 
    *Retrieve data from a REST API.
    *Transform and structure raw data using pandas
    *Prepare the data for relational database storage
    *Load processed data into MYSQL
    *Manage configuration through environement variables
    *Track pipeline execution using logs

Technologies Used
    *python3
    *Request
    *Pandas
    *MYSQL
    *mysql-connector-python
    *logging
    *python-dotenv

Project Structure

ecommerce-data-pipeline
|-- data/
|   |_ ecommerce_pipeline
|
|-- logs/
|   |_ pipeline.log
|
|-- src/
|   |_ database.py
|   |_ extract.py
|   |_ logger.py
|   |_ main.py
|   |_ sql.py
|   |_ transform.py
|
|.env.example
|README.md
|requirement.txt

Installation and setup

1.Clone the repository
git clone <url_repository>
2.Install dependencies
pip install -r requirement.txt
3. Create and configure the virtual environment
python -m venv .venv
Activate it:
-windows:
    .venv\Scripts\activate
-linux or macOS
    .venv/bin/activate
Create a ".env" file in the project root using .env.example as a template. 
Fill in the database configuration values required

Future improvements
    *Add automated tests
    *Containerize the application with Docker
    *Schedule automated pipeline runs

Author
    Joel

License 
    This project is intended for educational and portfolio purposes.