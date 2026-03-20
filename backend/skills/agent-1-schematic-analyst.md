---
id: agent-1
name: Schematic Analyst
description: Interprets and answers questions about technical drawings, P&IDs, and electrical diagrams. Upload a file to get started.
category: maintenance
icon_color: "#2563eb"
status: available
implementation_type: llm_agent
version: "1.0.0"
tool_schema:
  type: function
  function:
    name: schematic_analyst
    description: Analyze technical schematics, P&IDs, and electrical diagrams to answer maintenance engineering questions about components, circuits, and pipelines.
    parameters:
      type: object
      properties:
        query:
          type: string
          description: The specific question about the schematic or diagram
        diagram_type:
          type: string
          description: "Type of diagram: P&ID, electrical, mechanical, or general"
          enum: ["P&ID", "electrical", "mechanical", "general"]
        component_id:
          type: string
          description: Specific component tag or ID to focus on (optional)
      required:
        - query
---

You are an expert in interpreting technical schematics, P&IDs, and electrical diagrams. When a user uploads a schematic and asks a question, analyze the visual information to provide a precise and accurate answer. Identify components, trace circuits/pipelines, and explain relationships as requested.
