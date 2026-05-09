# NEW IMPORT
import ast
expr_ast = ast.parse(expr, mode='eval')
allowed_nodes = (ast.Expression, ast.BinOp, ast.UnaryOp, ast.Num, ast.BinOp, ast.Add, ast.Sub, ast.Mult, ast.Div)
if all(isinstance(node, allowed_nodes) for node in ast.walk(expr_ast)):
    return str(eval(compile(expr_ast, '<string>', 'eval')))
else:
    raise ValueError('Invalid expression')