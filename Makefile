fix-style:
	black aissist
	isort --profile black aissist

test:
	mypy --disallow-untyped-calls --disallow-untyped-defs --disallow-incomplete-defs aissist
	pylint --disable=C aissist
	black --check aissist
	pytest