"""
Sort list of classess in parent-child order
note that this does not take multiple inheritance into account
ref : https://stackoverflow.com/questions/34964878/python-generate-a-dictionarytree-from-a-list-of-tuples/35049729#35049729
with modification 
"""
import re
from typing import List

from loguru import logger as log

__all__ = ["sort_classes"]
RE_CLASS = re.compile(r"class\s+(?P<class>\w+)(\((?P<parent>\w*)\))?")


def sort_classes(classes: List[str]):
    "sort a list of classes to respect the parent-child order"
    # Note this only takes single decedents in perspective
    # pass 1: create nodes dictionary
    nodes = {"": {"id": "root", "children": []}}

    for c in classes:
        m = RE_CLASS.match(c)
        if m:
            # parent_name = m.group("parent")
            class_name = m.group("class").strip()
            nodes[class_name] = {"id": class_name, "class": c, "children": []}

    # pass 2: create trees and parent-child relations
    forest = []
    forest.append(nodes[""])  #  add root node to connect
    for c in classes:
        m = RE_CLASS.match(c)
        if not m:
            continue
        if m.group("parent"):  # parent specified
            parent_name = m.group("parent").split(",")[0].strip()  # just use first parent
        else:
            parent_name = ""

        class_name = m.group("class").strip()
        node = nodes[class_name]

        # either make the node a new tree or link it to its parent
        if class_name == parent_name:
            # start a new tree in the forest
            forest.append(node)
        else:
            # add new_node as child to parent
            try:
                parent = nodes[parent_name]
            except KeyError:
                # Parent not defined in this module, add as child to root
                parent = nodes[""]
            if not "children" in parent:
                # ensure parent has a 'children' field
                parent["children"] = []
            children = parent["children"]
            children.append(node)  # type:ignore

    # step 3: simple function to print
    def list_node(node, sorted: List[str]):
        try:
            sorted.append(node["class"])
            log.trace(node["id"], node["class"])
        except KeyError:
            log.trace(node["id"])
        log.trace(node["id"])
        if node.get("children", False):
            for child in node["children"]:
                list_node(child, sorted)

    sorted: List[str] = []

    for node in forest:
        list_node(node, sorted)
    return sorted
