import re

LOG_BUILD_MESSAGE = ["marked build as failure" ,"Execution failed for task"]
is_error = re.compile(r".*ERR.*|.*EXCEPTION.*|.*FAIL.*").match
output = {'errors': [], 'command': str()}


def check_for_pattern(line):
    if is_error(line.upper()):
        output['errors'].append(line)

def format_error(obj):
    log_exception = ""
    for line in obj:
        if len(line)>0 and '+' in line[0]:
            output['command'] = line[1:]
            break
        check_for_pattern(line)
        log_exception += line
    return log_exception

def build_exception_code(lines):
    index = 0
    log_exception = str()
    for line in lines[::-1]:
        if len([msg for msg in LOG_BUILD_MESSAGE if msg in line])>0:
            log_exception = format_error(lines[-index::-1])
            break
        index += 1
        continue
    return log_exception

def parse_consolee_log(console_output):
    build_exception_code(console_output)
    return output
