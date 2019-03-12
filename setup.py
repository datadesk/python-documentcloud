from setuptools import setup


setup(
    name='python-documentcloud',
    version='1.1.1',
    description='A simple Python wrapper for the DocumentCloud API',
    author='Ben Welsh',
    author_email='ben.welsh@gmail.com',
    url='http://datadesk.github.com/python-documentcloud/',
    license="MIT",
    packages=("documentcloud",),
    test_suite="tests.test_all",
    include_package_data=True,
    install_requires=(
        'python-dateutil>=2.1',
        'six>=1.4.1',
        'rfc3987',
    ),
    classifiers=(
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Topic :: Internet :: WWW/HTTP',
    )
)
