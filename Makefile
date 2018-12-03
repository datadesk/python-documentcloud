.PHONY: test ship


test:
	flake8 documentcloud
	coverage run setup.py test
	coverage report -m


ship:
	rm -rf build/
	python setup.py sdist bdist_wheel
	twine upload dist/* --skip-existing
