# ovbpclient

[Distribute to pip](https://medium.com/@joel.barmettler/how-to-upload-your-python-package-to-pypi-65edc5fe9c56):

!! don't forget to pull before doing this -> version file must be up to date (must be after jenkins workflow) !!

    python setup.py sdist
    twine upload dist/*

