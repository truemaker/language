import basic

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
            print(repr(result))
    # print(text)