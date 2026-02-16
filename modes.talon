# Mode switching commands — available in both command and dictation modes
mode: command
mode: dictation
-
^(dictation mode | mode dictation)$:
    mode.disable("sleep")
    mode.disable("command")
    mode.enable("dictation")
^(command mode | mode command)$:
    mode.disable("sleep")
    mode.disable("dictation")
    mode.enable("command")
^(mixed mode | mode mixed)$:
    mode.disable("sleep")
    mode.enable("command")
    mode.enable("dictation")
