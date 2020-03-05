import re
vars = []

with open('Dockerfile', 'r') as fp:
    lines = fp.readlines()
    for index, line in enumerate(lines):
        if line.startswith('ENV'):
            vars.append(line)
            for l in lines[index+1:]:
                if re.match(r'^\s+\w+', l):
                    vars.append(l)
                else:
                    break


def clean_up(line):
    s = re.sub(r'\s+|^ENV\s+|\\', '', line)
    s = 'export ' + s + '\n'
    return s


with open("env.sh", "w+") as f:
    for var in vars:
        f.write(clean_up(var))
