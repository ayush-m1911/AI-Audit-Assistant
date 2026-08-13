from langgraph.graph import StateGraph, START, END
from app.graph.state import AuditState
from app.graph.nodes import planner_node, retrieval_node, compliance_node, risk_node, recommendation_node

# Initialize StateGraph with the custom AuditState TypedDict
workflow = StateGraph(AuditState)

# Register planner, retriever, compliance, risk, and recommendation nodes
workflow.add_node("planner", planner_node)
workflow.add_node("retriever", retrieval_node)
workflow.add_node("compliance", compliance_node)
workflow.add_node("risk", risk_node)
workflow.add_node("recommendation", recommendation_node)

# Configure sequential execution edges
workflow.add_edge(START, "planner")
workflow.add_edge("planner", "retriever")
workflow.add_edge("retriever", "compliance")
workflow.add_edge("compliance", "risk")
workflow.add_edge("risk", "recommendation")
workflow.add_edge("recommendation", END)

# Compile workflow graph
audit_graph = workflow.compile()


