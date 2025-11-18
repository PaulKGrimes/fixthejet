from setuptools import setup

setup(name='fixthejet',
      version='1.0.0',
      description='Fix bad colormaps',
      url='http://github.com/kkraoj/fixthejet',
      author='Krishna Rao',
      author_email='kkrao dot j at g mail dot com',
      license='GPL-3.0',
      packages=['fixthejet'],
      install_requires=[
        'matplotlib >= 3.2.1',
        'numpy >= 1.19.4',
        'scipy >= 1.5.3'
      ],
      entry_points = {
            'console_scripts': ['fixthejet=fixthejet.fixthejet:main'],
        },   
      zip_safe=False)