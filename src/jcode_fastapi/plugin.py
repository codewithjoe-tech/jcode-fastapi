"""
FastAPI edge plugin for jcode.

Detects two patterns:

1. Depends(fn) / Security(fn) in function parameter defaults
   → DEPENDS edge: route handler → injected dependency function

2. Annotated[Type, Depends(fn)]
   → DEPENDS edge: route handler → injected dependency function

Because `Depends(get_current_user)` is a call node inside the *parameters*
of a route function, the generic parser already visits it. This plugin
intercepts the "Depends" callee name and emits a typed DEPENDS edge pointing
at the actual dependency function (the argument), not at Depends itself.
"""
from jcode.domain.models import Edge, Node, NodeId, NodeType
from jcode.storage.object_store import node_id_for

EDGE_DEPENDS = "depends"

_WRAPPER_NAMES = frozenset({"Depends", "Security", "Annotated"})


def _text(ts_node, source: bytes) -> str:
    return source[ts_node.start_byte:ts_node.end_byte].decode("utf-8", errors="replace")


def _provisional(name: str) -> Node:
    ph = Node(
        id=NodeId("0" * 64), node_type=NodeType.FUNCTION,
        name=name, title=name, file_path="<unresolved>",
        line_start=0, line_end=0,
    )
    return Node(
        id=node_id_for(ph), node_type=NodeType.FUNCTION,
        name=name, title=name, file_path="<unresolved>",
        line_start=0, line_end=0,
    )


class FastAPIPlugin:
    """Implements the jcode EdgePlugin protocol for FastAPI."""

    @property
    def handled_names(self) -> frozenset:
        return _WRAPPER_NAMES

    def handle_call(self, call_node, source: bytes, caller: Node):
        """
        For Depends(some_fn) emit:
          DEPENDS edge: caller → some_fn

        Handles both `Depends(fn)` and `Depends(dependency=fn)`.
        """
        arg_list = next(
            (c for c in call_node.children if c.type == "argument_list"), None
        )
        if arg_list is None:
            return [], []

        for arg in arg_list.children:
            if arg.type == "identifier":
                prov = _provisional(_text(arg, source))
                return [prov], [Edge(
                    source_id=caller.id, target_id=prov.id, edge_type=EDGE_DEPENDS,
                )]
            if arg.type == "keyword_argument":
                children = list(arg.children)
                if len(children) >= 3 and children[2].type == "identifier":
                    prov = _provisional(_text(children[2], source))
                    return [prov], [Edge(
                        source_id=caller.id, target_id=prov.id, edge_type=EDGE_DEPENDS,
                    )]

        return [], []


def create() -> FastAPIPlugin:
    return FastAPIPlugin()
