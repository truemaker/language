import sys
import basic

help_text = """
Sub commands:
    debug - shows the parse tree and the tokens
    help - shows this help
    shell - opens a normal shell session
    run - runs a program
"""

if len(sys.argv) > 1:
    if sys.argv[1] == 'debug':
        basic.debug = True
        if len(sys.argv) > 2:
            basic.run(sys.argv[1], 'run("' + sys.argv[2] + '")')
            sys.exit(0)
    elif sys.argv[1] == "help":
        print(help_text)
        sys.exit(0)
    elif sys.argv[1] == "shell":
        pass
    elif sys.argv[1] == "run":
        if len(sys.argv) > 2:
            basic.run(sys.argv[1], 'run("' + sys.argv[2] + '")')
        else:
            print("Usage: shell run <filename>\n" + help_text)
        sys.exit(0)
    else:
        print("Usage: shell <subcommand>\n" + help_text)
        sys.exit(0)
else:
    print("Usage: shell <subcommand>\n" + help_text)
    sys.exit(0)

while True:
    text = input("basic> ")
    if text.strip() == '':
        continue
    result, err = basic.run('<stdin>', text)
    if err:
        print(err.as_string())
    elif result:
        if len(result.elements) == 1:
            print(result.elements[0])
        else:
            print(str(result))
    # print(text)
