"""
Dead code detector - finds unused functions.
Works for ALL languages (language-agnostic).
"""

from typing import Dict, List, Set


class DeadCodeAnalyzer:
    """
    Detects dead code (unused functions) in a repository.
    Language-agnostic: works on call graph structure.
    """

    def __init__(self, repository_id: str):
        self.repository_id = repository_id

    def find_dead_functions(self, call_graph: Dict) -> List[Dict]:
        """
        Find functions that are never called (potential dead code).

        Args:
            call_graph: Output from CallGraphAnalyzer.build_call_graph()

        Returns:
            List of dead functions with details
        """
        nodes = call_graph["nodes"]
        entry_points = {
            "main",
            "__init__",
            "__main__",
            "init",
            "setup",
            "start",
            "Main",
            "MAIN",
            "MAIN-PARAGRAPH",
            "START",
            "_start",
        }
        dead_functions = []
        for node in nodes:
            function_name = node["name"]
            called_by = node.get("called_by", [])
            is_external = node.get("is_external", False)
            if is_external:
                continue
            if function_name in entry_points or function_name.lower() in {
                e.lower() for e in entry_points
            }:
                continue
            if function_name.startswith("__") and function_name.endswith("__"):
                continue
            if len(called_by) == 0:
                dead_functions.append(
                    {
                        "name": function_name,
                        "file": node["file"],
                        "symbol_id": node["symbol_id"],
                        "calls": len(node.get("calls", [])),
                        "severity": (
                            "high" if len(node.get("calls", [])) == 0 else "medium"
                        ),
                    }
                )
        return sorted(dead_functions, key=lambda x: x["severity"], reverse=True)

    def find_circular_dependencies(self, call_graph: Dict) -> List[Dict]:
        """
        Find circular dependencies (A calls B, B calls A).

        Args:
            call_graph: Call graph structure

        Returns:
            List of circular dependency cycles
        """
        nodes = {node["name"]: node for node in call_graph["nodes"]}
        cycles = []
        visited = set()

        def dfs(node_name: str, path: List[str], path_set: Set[str]):
            """Depth-first search to detect cycles."""
            if node_name in path_set:
                cycle_start = path.index(node_name)
                cycle = path[cycle_start:] + [node_name]
                if len(cycle) > 2:
                    cycles.append(cycle)
                return
            if node_name in visited or node_name not in nodes:
                return
            visited.add(node_name)
            path.append(node_name)
            path_set.add(node_name)
            for callee in nodes[node_name].get("calls", []):
                dfs(callee, path.copy(), path_set.copy())
            path.pop()
            path_set.remove(node_name)

        for node_name in nodes.keys():
            if node_name not in visited:
                dfs(node_name, [], set())
        unique_cycles = []
        seen_cycles = set()
        for cycle in cycles:
            normalized = tuple(sorted(cycle))
            if normalized not in seen_cycles:
                seen_cycles.add(normalized)
                unique_cycles.append(
                    {
                        "cycle": cycle,
                        "length": len(cycle) - 1,
                        "severity": "critical" if len(cycle) - 1 <= 3 else "high",
                    }
                )
        return sorted(unique_cycles, key=lambda x: x["length"])
