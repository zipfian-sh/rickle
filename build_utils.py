import subprocess
import unittest

from datetime import datetime

_project_name = 'rickle'

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def specified_tests(tests):
    for test in tests:
        file_name = '%s.py' % test
        tests = unittest.TestLoader().discover(start_dir="./tests/unittest", pattern=file_name, top_level_dir=".")
        unittest.TextTestRunner(verbosity=4).run(tests)
        tests = unittest.TestLoader().discover(start_dir="./tests/integration", pattern=file_name, top_level_dir=".")
        unittest.TextTestRunner(verbosity=4).run(tests)

def all_unit_tests(do_coverage=False):
    import coverage
    print(f'{bcolors.UNDERLINE}{bcolors.BOLD}{bcolors.HEADER}-- Running all unit tests!{bcolors.ENDC}')
    cov = coverage.Coverage(cover_pylib=False, data_file='.unittest')
    if do_coverage:
        cov.start()

    tests = unittest.TestLoader().discover(start_dir="./tests/unittest", pattern="test_*.py", top_level_dir=".")
    result = unittest.TextTestRunner(verbosity=4).run(tests)
    if do_coverage:
        cov.stop()
        cov.save()
        cov.html_report(directory='coverage_report/unittests')
    return result.wasSuccessful()

def all_integration_tests(do_coverage=False):
    import coverage
    print(f'{bcolors.UNDERLINE}{bcolors.BOLD}{bcolors.HEADER}-- Running all integration tests!{bcolors.ENDC}')
    cov = coverage.Coverage(cover_pylib=False, data_file='.integration')
    if do_coverage:
        cov.start()

    tests = unittest.TestLoader().discover(start_dir="./tests/integration", pattern="test_*.py", top_level_dir=".")
    result = unittest.TextTestRunner(verbosity=4).run(tests)
    if do_coverage:
        cov.stop()
        cov.save()
        cov.html_report(directory='coverage_report/integration')
    return result.wasSuccessful()

def bump_version_patch(with_poetry=True):
    if with_poetry:
        result = subprocess.Popen("poetry version patch -s",
                                  shell=True,
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE,
                                  text=True)
        version_name = result.stdout.read().strip()

        with open(f"{_project_name}/__version__.py", "r") as f:
            lines = f.readlines()
            lines[0] = f"__version__ = '{version_name}'\n"
            lines[1] = f'__date__ = "{datetime.today().strftime("%Y-%m-%d")}"\n'
        if lines:
            with open(f"{_project_name}/__version__.py", "w") as f:
                f.writelines(lines)
    else:

        with open(f"{_project_name}/__version__.py", "r") as f:
            lines = f.readlines()
            v = version_name.split('.')
            major = int(v[0])
            minor = int(v[1])
            patch = int(v[2]) + 1
            lines[0] = f"__version__ = '{major}.{minor}.{patch}'\n"
            lines[1] = f'__date__ = "{datetime.today().strftime("%Y-%m-%d")}"\n'
        if lines:
            with open(f"{_project_name}/__version__.py", "w") as f:
                f.writelines(lines)

    print(f"{bcolors.OKGREEN}{bcolors.BOLD}-- Version number bumped to {version_name}!{bcolors.ENDC}")