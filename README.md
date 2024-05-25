## Getting Started

This project is built using Flask for the API.
To run this project on production, follow these instructions:

```bash
# Clone the repository
git clone https://github.com/BioCloudLabs/blast-control.git

# Navigate to the project directory
cd blast-control

# Create a virtual env (install python3-venv if is not alredy installed):
python3 -m venv .venv

# Use the venv:
. .venv/bin/activate

# Install all the requirements
pip install -r requirements.txt

# Run gunicorn: 
gunicorn -w 2 -b 0.0.0.0:4000 --timeout 999999 app:app

# Now the blast-control part of the project will be up and working.
```

## IMPORTANT INFO
- This project needs azure-cli installed on the server, to install it, follow these instructions:
- https://learn.microsoft.com/en-us/cli/azure/install-azure-cli-linux
