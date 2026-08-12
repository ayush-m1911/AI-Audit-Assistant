from langgraph.graph import StateGraph, START, END
from app.graph.state import AuditState
from app.graph.nodes import planner_node, retrieval_node

# Initialize StateGraph with the custom AuditState TypedDict
workflow = StateGraph(AuditState)

# Register planner and retriever nodes
workflow.add_node("planner", planner_node)
workflow.add_node("retriever", retrieval_node)

# Configure sequential edges
workflow.add_edge(START, "planner")
workflow.add_edge("planner", "retriever")
workflow.add_edge("retriever", END)

# Compile workflow graph
audit_graph = workflow.compile()
