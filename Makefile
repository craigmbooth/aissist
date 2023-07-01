fix-style:
	black aissist
	isort --profile black aissist

test:
	mypy aissist