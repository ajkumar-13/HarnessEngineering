"""One MCP tool call inside the act step: the JSON-RPC frame the client sends, and what the loop gets back.

Run from the series root:  uv run python posts/07-skills-mcp-runtime/snippets/mcp_dispatch.py
No server and no SDK: StubClient prints the request a real client would write to the transport and returns a
canned result in the specification's shape; DownClient times out, as an unreachable server does.
"""
import json

class StubClient:
    """Stands in for a real JSON-RPC client so this snippet runs on its own."""
    def __init__(self):
        self.next_id = 1

    def request(self, method: str, params: dict) -> dict:
        params = {**params, "_meta": {"io.modelcontextprotocol/protocolVersion": "2026-07-28",
                                      "io.modelcontextprotocol/clientCapabilities": {}}}  # on every request
        frame = {"jsonrpc": "2.0", "id": self.next_id, "method": method, "params": params}
        self.next_id += 1
        print("client sends:  ", json.dumps(frame))
        return {"resultType": "complete", "content": [{"type": "text", "text": "TICKET-4417 created"}],
                "isError": False}

class DownClient(StubClient):
    def request(self, method: str, params: dict) -> dict:
        raise TimeoutError("no response in 30 s")

def validate(result: dict) -> dict:
    if not isinstance(result, dict) or not isinstance(result.get("content"), list):
        return {"error": "malformed tool result"}
    if result.get("isError"):
        return {"error": "tool reported an error", "content": result["content"]}
    return result

def call_mcp_tool(client, name: str, arguments: dict) -> dict:
    try:
        result = client.request("tools/call", {"name": name, "arguments": arguments})
    except (TimeoutError, ConnectionError) as exc:
        return {"error": f"{name} unavailable: {exc}"}   # a corrigible observation, not a crash
    return validate(result)   # server output is untrusted input


if __name__ == "__main__":
    args = {"title": "Disk full on web-03"}
    print("observation:   ", json.dumps(call_mcp_tool(StubClient(), "create_ticket", args)))
    print("server down:   ", json.dumps(call_mcp_tool(DownClient(), "create_ticket", args)))
    print("bad result:    ", json.dumps(validate({"text": "TICKET-4417 created"})))
