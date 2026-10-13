import ast
import re
import os
import base64

class PythonDeobfuscator:
    def __init__(self):
        self.name_map = {}
        self.reverse_map = {}

    def deobfuscate_file(self, input_path, output_path=None):
        if not os.path.exists(input_path):
            print(f"[!] File not found: {input_path}")
            return False

        with open(input_path, 'r', encoding='utf-8', errors='ignore') as f:
            source = f.read()

        deobfuscated = self._deobfuscate_source(source)

        if output_path is None:
            base, ext = os.path.splitext(input_path)
            output_path = f"{base}_deobfuscated{ext}"

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(deobfuscated)

        print(f"[+] Deobfuscated file saved to: {output_path}")
        return True

    def _deobfuscate_source(self, source):
        lines = source.split('\n')
        deobfuscated_lines = []
        for line in lines:
            if line.strip().startswith('#'):
                deobfuscated_lines.append(line)
                continue
            deobfuscated_lines.append(self._deobfuscate_line(line))
        return '\n'.join(deobfuscated_lines)

    def _deobfuscate_line(self, line):
        line = re.sub(r"__import__\('base64'\)\.b64decode\('([^']+)'\)\.decode\('utf-8'\)", self._decode_base64, line)
        line = re.sub(r"base64\.b64decode\('([^']+)'\)\.decode\('utf-8'\)", self._decode_base64, line)
        return line

    def _decode_base64(self, match):
        encoded = match.group(1)
        try:
            decoded = base64.b64decode(encoded).decode('utf-8')
            return f"'{decoded}'"
        except Exception:
            return match.group(0)
