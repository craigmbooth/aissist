fix-style:
	black aissist
	isort --profile black aissist

test:
	mypy --strict aissist