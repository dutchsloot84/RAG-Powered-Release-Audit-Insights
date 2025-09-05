.PHONY: fmt test ui audit

fmt:
black app tests main.py
ruff app tests main.py --fix

test:
pytest -q

ui:
streamlit run app/ui/ui_app.py

audit:
python main.py --jql "$(JQL)" --repos "$(REPOS)" --branches "$(BRANCHES)" --update-cache
