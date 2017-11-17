import re
import warnings

from path import Path

SETTINGS = [dict(ext  = [".bat"],
                 left =  r':: '),
            dict(ext  = [".sh", ".py", ".yaml", ".yml"],
                 left =  '## '),
            dict(ext  = [".c", ".cc", ".cpp", ".c++", ".h"],
                 left = r'// '),
            dict(ext  = [".rst"],
                 left = r'.. ')]

for index, SETTING in enumerate(SETTINGS):
    if 'right' not in SETTING and 'left' in SETTING:
        SETTING['right'] = ''.join(reversed(SETTING['left']))
    elif 'left' not in SETTING and 'right' in SETTING:
        SETTING['left'] = ''.join(reversed(SETTING['right']))
    elif 'left' not in SETTING and 'right' not in SETTING:
        raise ValueError('invalid setting at position ' + str(index))

SETTINGS = {ext : SETTING for SETTING in SETTINGS for ext in SETTING['ext']}
SETTINGS['SConstruct'] = SETTINGS['.py']
SETTINGS['SConscript'] = SETTINGS['.py']


def find_notice(filepath):
    if not isinstance(filepath, Path):
        filepath = Path(filepath)
    if not(filepath.exists() or filepath.isfile()):
        raise ValueError("'filepath' parameter is not a valid path to a file")
    start = 0
    end = -1
    SETTING = SETTINGS.get(filepath.ext, SETTINGS.get(filepath.basename(), None))
    if SETTING is None:
        warnings.warn("No settings found for file '" + filepath + "'")
    else:
        with open(filepath, 'r') as filehandler:
            pattern = re.compile('^' + SETTING['left'] + '.*' + SETTING['right'] + '$')
            start = 0
            # import pdb
            # pdb.set_trace()
            line = filehandler.readline()
            while line and not pattern.match(line):
                start += 1
                line = filehandler.readline()
            if not line:
                start = 0
            else:
                end = start
                line = filehandler.readline()
                while line  and pattern.match(filehandler.readline()):
                    end += 1
                    line = filehandler.readline()
                if not line:
                    start = 0
                    end = -1
    return start, end

def generate_notice(filepath, notice):
    if not isinstance(filepath, Path):
        filepath = Path(filepath)
    if not(filepath.exists() or filepath.isfile()):
        raise ValueError("'filepath' parameter is not a valid path to a file")
    SETTING = SETTINGS.get(filepath.ext, SETTINGS.get(filepath.basename(), None))
    if SETTING is None:
        warnings.warn("No settings found for file '" + filepath + "'")
        return []
    else:
        lines = notice.splitlines()
        max_width = 0
        for line in lines:
            max_width = max(max_width, len(line))
        return [SETTING["left"] + line + " " * (max_width - len(line)) + SETTING["right"] + "\n" for line in lines]

def insert_notice(filepath, notice, back_up=False):
    if not isinstance(filepath, Path):
        filepath = Path(filepath)
    if not(filepath.exists() or filepath.isfile()):
        raise ValueError("'filepath' parameter is not a valid path to a file")
    SETTING = SETTINGS.get(filepath.ext, SETTINGS.get(filepath.basename(), None))
    if SETTING is None:
        warnings.warn("No settings found for file '" + filepath + "'")
    else:
        with open(filepath, "r") as filehandler:
            lines = list(filehandler.readlines())
        if back_up:
            with open(filepath + ".back", "w") as filehandler:
                filehandler.writelines(lines)
        if len(lines) > 0:
            start, end = find_notice(filepath)
            lines = lines[:start] + generate_notice(filepath, notice) + ["\n"] * bool(lines[end + 1].strip()) + lines[end + 1:]
        else:
            lines = generate_notice(filepath, notice)
        with open(filepath, "w") as filehandler:
            filehandler.writelines(lines)