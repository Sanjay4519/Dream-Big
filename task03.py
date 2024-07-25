
def remove_html_markup(s):
    tag = 0
    out = ""

    for c in s:
        if c == '<':
            tag += 1
        elif c == '>':
            tag -= 1
        elif tag == 0:
            out = out + c

    return out


print(remove_html_markup("Here's some <strong>strong argument</strong>."))
print(remove_html_markup('<input type="text" value="<your name>">'))