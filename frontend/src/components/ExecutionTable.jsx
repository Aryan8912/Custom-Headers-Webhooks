import StatusBadge from "./StatusBadge";

const ExecutionTable = ({ data, isLoading, onSelect }) => {
  if (isLoading) {
    return (
      <div style={{ textAlign: "center", padding: "48px", color: "#6b7280" }}>
        Loading executions...
      </div>
    );
  }

  if (!data?.items?.length) {
    return (
      <div style={{ textAlign: "center", padding: "48px", color: "#6b7280" }}>
        No executions found.
      </div>
    );
  }

  return (
    <div style={{ overflowX: "auto" }}>
      <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "14px" }}>
        <thead>
          <tr style={{ background: "#f9fafb", borderBottom: "1px solid #e5e7eb" }}>
            <th style={th}>Execution ID</th>
            <th style={th}>Agent ID</th>
            <th style={th}>Status</th>
            <th style={th}>Auth</th>
            <th style={th}>Forwarded</th>
            <th style={th}>Created At</th>
            <th style={th}>Actions</th>
          </tr>
        </thead>
        <tbody>
          {data.items.map((item) => (
            <tr
              key={item.id}
              style={{ borderBottom: "1px solid #e5e7eb", transition: "background 0.15s" }}
              onMouseEnter={e => e.currentTarget.style.background = "#f9fafb"}
              onMouseLeave={e => e.currentTarget.style.background = "white"}
            >
              <td style={td}>
                <span style={{ fontFamily: "monospace", fontSize: "12px", color: "#6b7280" }}>
                  {item.execution_id.slice(0, 16)}...
                </span>
              </td>
              <td style={td}>{item.agent_id}</td>
              <td style={td}><StatusBadge status={item.status} /></td>
              <td style={td}>
                <span style={{ color: item.auth_verified ? "#059669" : "#dc2626", fontWeight: "600" }}>
                  {item.auth_verified ? "✓ Verified" : "✗ Failed"}
                </span>
              </td>
              <td style={td}>
                <span style={{ color: item.forwarded ? "#059669" : "#6b7280" }}>
                  {item.forwarded ? "✓ Yes" : "— No"}
                </span>
              </td>
              <td style={td}>
                <span style={{ color: "#6b7280", fontSize: "12px" }}>
                  {new Date(item.created_at).toLocaleString()}
                </span>
              </td>
              <td style={td}>
                <button
                  onClick={() => onSelect(item.execution_id)}
                  style={{
                    background: "#6c63ff",
                    color: "white",
                    border: "none",
                    padding: "4px 12px",
                    borderRadius: "4px",
                    fontSize: "12px",
                    cursor: "pointer",
                  }}
                >
                  View
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

const th = {
  padding: "12px 16px",
  textAlign: "left",
  fontWeight: "600",
  color: "#374151",
  fontSize: "12px",
  textTransform: "uppercase",
  letterSpacing: "0.05em",
};

const td = {
  padding: "12px 16px",
  color: "#111827",
};

export default ExecutionTable;