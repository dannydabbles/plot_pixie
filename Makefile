# Makefile for Streamlit application.

# Variables
ST_APP=main.py

.PHONY: help clean lint

# Help command
help:
	@echo "Makefile for Streamlit application."
	@echo "-------------------------------------------------------------------"
	@echo "The following commands are available:"
	@echo " - run: Start Streamlit application"
	@echo " - lint: Lint your Streamlit application using flake8"

# Run Streamlit application
run:
	streamlit run $(ST_APP) --logger.level=debug

# Lint Streamlit application using flake8
lint:
	flake8 $(ST_APP)
