import ast
import base64
import random
import string
import os

class PythonObfuscator:
    def __init__(self):
        self.var_map = {}
        self.used_names = set()
        self.imports = []
        self.string_encryptor_key = self._gen_key(16)

    def _gen_key(self, length):
        return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length))

    def _obfuscate_string(self, s):
        encoded = base64.b64encode(s.encode('utf-8')).decode('utf-8')
        return f"__import__('base64').b64decode('{encoded}').decode('utf-8')"

    def _obfuscate_name(self, name):
        if name in self.var_map:
            return self.var_map[name]
        if name.startswith('__') or name in ('self', 'cls', 'super'):
            return name
        new_name = '_' + ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(8))
        while new_name in self.used_names:
            new_name = '_' + ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(8))
        self.var_map[name] = new_name
        self.used_names.add(new_name)
        return new_name

    def obfuscate_file(self, input_path, output_path=None):
        if not os.path.exists(input_path):
            print(f"[!] File not found: {input_path}")
            return False

        with open(input_path, 'r', encoding='utf-8', errors='ignore') as f:
            source = f.read()

        try:
            tree = ast.parse(source)
        except SyntaxError as e:
            print(f"[!] Syntax error in source: {e}")
            return False

        obfuscated = self._obfuscate_node(tree)
        obfuscated_source = ast.unparse(obfuscated)

        if output_path is None:
            base, ext = os.path.splitext(input_path)
            output_path = f"{base}_obfuscated{ext}"

        header = f"# Obfuscated by Mainframe Python Obfuscator\n"
        header += f"import base64\n"
        header += f"_key = '{self.string_encryptor_key}'\n\n"

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(header + obfuscated_source)

        print(f"[+] Obfuscated file saved to: {output_path}")
        return True

    def _obfuscate_node(self, node):
        if isinstance(node, ast.Module):
            node.body = [self._obfuscate_node(n) for n in node.body]
            return node
        elif isinstance(node, ast.FunctionDef):
            node.name = self._obfuscate_name(node.name)
            node.args.args = [ast.arg(arg=self._obfuscate_name(a.arg), annotation=a.annotation) for a in node.args.args]
            node.body = [self._obfuscate_node(n) for n in node.body]
            return node
        elif isinstance(node, ast.ClassDef):
            node.name = self._obfuscate_name(node.name)
            node.body = [self._obfuscate_node(n) for n in node.body]
            return node
        elif isinstance(node, ast.Assign):
            node.targets = [self._obfuscate_node(t) for t in node.targets]
            node.value = self._obfuscate_node(node.value)
            return node
        elif isinstance(node, ast.Name):
            node.id = self._obfuscate_name(node.id)
            return node
        elif isinstance(node, ast.Constant):
            if isinstance(node.value, str):
                encrypted = ''.join(chr(ord(c) ^ ord(self.string_encryptor_key[i % len(self.string_encryptor_key)])) for i, c in enumerate(node.value))
                encoded = base64.b64encode(encrypted.encode('utf-8')).decode('utf-8')
                return ast.parse(f"__import__('base64').b64decode('{encoded}').decode('utf-8')").body[0].value
            return node
        elif isinstance(node, ast.Expr):
            node.value = self._obfuscate_node(node.value)
            return node
        elif isinstance(node, ast.Return):
            node.value = self._obfuscate_node(node.value) if node.value else None
            return node
        elif isinstance(node, ast.If):
            node.test = self._obfuscate_node(node.test)
            node.body = [self._obfuscate_node(n) for n in node.body]
            if node.orelse:
                node.orelse = [self._obfuscate_node(n) for n in node.orelse]
            return node
        elif isinstance(node, ast.For):
            node.target = self._obfuscate_node(node.target)
            node.iter = self._obfuscate_node(node.iter)
            node.body = [self._obfuscate_node(n) for n in node.body]
            return node
        elif isinstance(node, ast.While):
            node.test = self._obfuscate_node(node.test)
            node.body = [self._obfuscate_node(n) for n in node.body]
            return node
        elif isinstance(node, ast.Call):
            node.func = self._obfuscate_node(node.func)
            node.args = [self._obfuscate_node(a) for a in node.args]
            node.keywords = [self._obfuscate_node(k) for k in node.keywords]
            return node
        elif isinstance(node, ast.BinOp):
            node.left = self._obfuscate_node(node.left)
            node.right = self._obfuscate_node(node.right)
            return node
        elif isinstance(node, ast.Compare):
            node.left = self._obfuscate_node(node.left)
            node.comparators = [self._obfuscate_node(c) for c in node.comparators]
            return node
        elif isinstance(node, ast.BoolOp):
            node.values = [self._obfuscate_node(v) for v in node.values]
            return node
        elif isinstance(node, ast.List):
            node.elts = [self._obfuscate_node(e) for e in node.elts]
            return node
        elif isinstance(node, ast.Dict):
            node.keys = [self._obfuscate_node(k) for k in node.keys]
            node.values = [self._obfuscate_node(v) for v in node.values]
            return node
        elif isinstance(node, ast.Attribute):
            node.value = self._obfuscate_node(node.value)
            return node
        elif isinstance(node, ast.Subscript):
            node.value = self._obfuscate_node(node.value)
            node.slice = self._obfuscate_node(node.slice)
            return node
        elif isinstance(node, ast.Import):
            node.names = [ast.alias(name=n.name, asname=self._obfuscate_name(n.asname or n.name)) for n in node.names]
            return node
        elif isinstance(node, ast.ImportFrom):
            node.names = [ast.alias(name=n.name, asname=self._obfuscate_name(n.asname or n.name)) for n in node.names]
            return node
        elif isinstance(node, ast.Raise):
            if node.exc:
                node.exc = self._obfuscate_node(node.exc)
            return node
        elif isinstance(node, ast.Assert):
            node.test = self._obfuscate_node(node.test)
            if node.msg:
                node.msg = self._obfuscate_node(node.msg)
            return node
        elif isinstance(node, ast.AugAssign):
            node.target = self._obfuscate_node(node.target)
            node.value = self._obfuscate_node(node.value)
            return node
        elif isinstance(node, ast.UnaryOp):
            node.operand = self._obfuscate_node(node.operand)
            return node
        elif isinstance(node, ast.IfExp):
            node.test = self._obfuscate_node(node.test)
            node.body = self._obfuscate_node(node.body)
            node.orelse = self._obfuscate_node(node.orelse)
            return node
        elif isinstance(node, ast.FunctionDef):
            node.name = self._obfuscate_name(node.name)
            node.args.args = [ast.arg(arg=self._obfuscate_name(a.arg), annotation=a.annotation) for a in node.args.args]
            node.body = [self._obfuscate_node(n) for n in node.body]
            return node
        elif isinstance(node, ast.AsyncFunctionDef):
            node.name = self._obfuscate_name(node.name)
            node.args.args = [ast.arg(arg=self._obfuscate_name(a.arg), annotation=a.annotation) for a in node.args.args]
            node.body = [self._obfuscate_node(n) for n in node.body]
            return node
        elif isinstance(node, ast.Lambda):
            node.args.args = [ast.arg(arg=self._obfuscate_name(a.arg), annotation=a.annotation) for a in node.args.args]
            node.body = self._obfuscate_node(node.body)
            return node
        elif isinstance(node, ast.Tuple):
            node.elts = [self._obfuscate_node(e) for e in node.elts]
            return node
        elif isinstance(node, ast.Set):
            node.elts = [self._obfuscate_node(e) for e in node.elts]
            return node
        elif isinstance(node, ast.Yield):
            if node.value:
                node.value = self._obfuscate_node(node.value)
            return node
        elif isinstance(node, ast.YieldFrom):
            node.value = self._obfuscate_node(node.value)
            return node
        elif isinstance(node, ast.Await):
            node.value = self._obfuscate_node(node.value)
            return node
        elif isinstance(node, ast.FormattedValue):
            node.value = self._obfuscate_node(node.value)
            return node
        elif isinstance(node, ast.JoinedStr):
            node.values = [self._obfuscate_node(v) for v in node.values]
            return node
        else:
            return node
