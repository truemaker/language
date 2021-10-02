import sys
import basic

if len(sys.argv) > 1:
    basic.run(sys.argv[1], 'run("' + sys.argv[1] + '")')
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