#!/usr/bin/python

import os
import re
import sys
import getopt


def run_checkstyle(file_name, checkstyle, project_dir):
    output = os.popen("(cd " + project_dir + "; \
        java -jar checkstyle.jar \
        -c " + checkstyle + " \
         " + file_name + ")").read()
    output = output.split("\n")
    length = len(output)
    return output[1:length - 2]  # remove first and last line


def find_changed_lines(git_diff):  # returns changed line numbers
    changed_lines_pattern = "@@ [0-9\-+,]+ ([0-9\-+,]+) @@"
    lines = []
    for change in re.findall(changed_lines_pattern, git_diff):
        value = change.split(",")
        if len(value) == 1:  # one line changed
            line_number = (value[0])
            lines.append(int(line_number))
        elif len(value) == 2:  # more lines changed
            line_number = int(value[0])
            count = int(value[1])
            for i in range(line_number, line_number + count):
                lines.append(i)
    return lines


def filter_out(processed_line):  # True when file should be filtered out
    column = processed_line.split("\t")
    if len(column) != 3:
        return True
    added_lines = column[0]
    name = column[2]
    return not name.endswith(".java") or not added_lines.isdigit() or not int(added_lines) > 0


def get_file_name(processed_line):
    return processed_line.split("\t")[2]


def introduced_error(error_message, changed_lines, out):
    line_pattern = ":(\d+):"
    number = re.search(line_pattern, error_message).group(1)
    number = int(number)
    if number in changed_lines:
        print "Introduced Error: " + error_message
        out.append(error_message)
    else:
        print "Warning: " + error_message


def usage():
    return "checkstyle -c <checkstyle.xml> -d <project directory> -h <help>"


def main(argv):
    try:
        opts, args = getopt.getopt(argv, "c:d:hx")
    except getopt.GetoptError:
        print usage()
        sys.exit(2)

    checkstyle_rules = "checkstyle-rules.xml"
    project_dir = "."
    debug = False

    for opt, arg in opts:
        if opt == "-c":
            checkstyle_rules = arg
        elif opt == "-d":
            project_dir = arg
        elif opt == "-h":
            print usage()
        elif opt == "-x":
            debug = True

    if debug:
        print "dir: " + project_dir + " rules: " + checkstyle_rules

    diff_command = "(cd " + project_dir + "; git diff HEAD^ --numstat)"

    print "Processing"

    errors = []
    list_of_files = os.popen(diff_command).read().split("\n")
    for file_line in list_of_files:
        if filter_out(file_line):
            # skip non java files and without added lines
            continue
        file_name = get_file_name(file_line)
        if debug:
            print "check " + file_name

        # get changed lines
        changes = os.popen("(cd " + project_dir + "; git diff -U0 HEAD^ " + file_name + ")").read()
        lines = find_changed_lines(changes)
        checkstyle = run_checkstyle(file_name, checkstyle_rules, project_dir)
        for item in checkstyle:
            # extract errors introduced in added lines and append errors list
            introduced_error(item, lines, errors)

    if errors:
        print "Errors in added lines:"
        for item in errors:
            print item
        sys.exit(1)


if __name__ == "__main__":
    main(sys.argv[1:])