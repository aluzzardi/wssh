from setuptools import setup


setup(
    name='wssh',
    version='0.0.1',
    author='Andrea Luzzardi <aluzzardi@gmail.com>',
    packages=[
        'wssh'
        ],
    scripts=[
        'bin/wssh',
        'bin/wsshd'
        ],
    package_data={'': ['static/*', 'templates/*']},
    include_package_data=True,
    zip_safe=False
)
