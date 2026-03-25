"""Shared utilities for console tree rendering."""


def print_ascii_tree(root) -> None:
    """Print a binary tree using ASCII branch connectors."""
    if root is None:
        print("El arbol esta vacio.")
        return

    _print_node(root, "", True)


def _print_node(node, prefix: str, is_left: bool) -> None:
    """Recursive helper for print_ascii_tree."""
    if node is None:
        return

    if node.getRightChild():
        new_prefix = prefix + ("|   " if is_left else "    ")
        _print_node(node.getRightChild(), new_prefix, False)

    connector = "\\-- " if is_left else "/-- "
    print(prefix + connector + str(node.getValue()))

    if node.getLeftChild():
        new_prefix = prefix + ("    " if is_left else "|   ")
        _print_node(node.getLeftChild(), new_prefix, True)
