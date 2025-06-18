columns = {
    "id": "uuid PRIMARY KEY",
    "message": "text",
    "created_at": "timestamp"
}
column_defs = ', '.join([f"{k} {v}" for k, v in columns.items()])
print("Sending column defs:", column_defs)
response = agent.create_table("demo_logs", columns)
print("Response:", response)
