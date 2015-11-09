from setuptools import setup

exec(open('slackn/version.py').read())

requirements = [ 'redis>=2.10.5' ]

setup(
    name='slackn',
    version=version,
    packages=['slackn'],
    description='Nagios batch notifier for Slack',
    author='Bradley Cicenas',
    author_email='bradley.cicenas@gmail.com',
    url='https://github.com/bcicen/slackn',
    install_requires=requirements,
    license='http://opensource.org/licenses/MIT',
    classifiers=(
        'License :: OSI Approved :: MIT License ',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Development Status :: 5 - Production/Stable',
    ),
    keywords='slack nagios devops',
    entry_points={'console_scripts': ['slackn-notify = slackn.cli:notify',
                                      'slackn-process = slackn.cli:process'] }
)
