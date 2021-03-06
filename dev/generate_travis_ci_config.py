#!/usr/bin/env python
import glob
import os
from jinja2 import Template


def _get_test_files(directory):
    return glob.glob("{}/test_*.py".format(directory))


def _split(a, n):
    k, m = divmod(len(a), n)
    return (
        a[i * k + min(i, m) : (i + 1) * k + min(i + 1, m)] for i in range(n)
    )


def _chunks(l, n):
    n = max(1, n)
    return (l[i : i + n] for i in range(0, len(l), n))


if __name__ == "__main__":
    print("Generating Travis CI configuration...")

    script_directory = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_directory)

    test_files = _get_test_files(
        os.path.abspath(os.path.join("..", "tests", "integration"))
    )
    test_files.sort()
    relative_files = [os.path.relpath(f, "..") for f in test_files]

    parts = int(os.environ.get("TEST_JOBS", 4))
    testset = _split(relative_files, parts)

    print(
        "Testset contains [{}] files for [{}] jobs".format(
            len(test_files), parts
        )
    )

    template_path = os.path.abspath(os.path.join("..", ".travis.yml.j2"))

    generated_notice = """# This file is autogenerated from {}
#
#   To generate, run {}
#
""".format(
        os.path.relpath(template_path, ".."), __file__,
    )

    print("Using [{}] as template...".format(template_path))
    with open(template_path, "r") as file_:
        template = Template(file_.read())
    rendered = template.render(
        generated_notice=generated_notice, testset=testset,
    )

    output_path = os.path.abspath(os.path.join("..", ".travis.yml"))
    with open(output_path, "w") as file_:
        file_.write(rendered)

    print("Travis CI configuration written to [{}]".format(output_path))
