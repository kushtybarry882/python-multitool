import sys

if sys.platform == 'win32':
    try:
        import msvcrt

        def get_input(prompt):
            sys.stdout.write(prompt)
            sys.stdout.flush()
            buf = ""
            while True:
                ch = msvcrt.getwch()
                if ch == '\x00' or ch == '\xe0':
                    msvcrt.getwch()
                    continue
                if ch == '\x1b':
                    print()
                    return "back"
                if ch == '\r':
                    print()
                    break
                if ch == '\b':
                    if buf:
                        buf = buf[:-1]
                        sys.stdout.write('\b \b')
                        sys.stdout.flush()
                    continue
                buf += ch
                sys.stdout.write(ch)
                sys.stdout.flush()
            return buf.strip()

    except ImportError:
        def get_input(prompt):
            try:
                return input(prompt).strip()
            except EOFError:
                return "back"
else:
    def get_input(prompt):
        try:
            value = input(prompt).strip()
        except EOFError:
            return "back"
        if value.lower() in ("esc", "back", "return"):
            return "back"
        return value
