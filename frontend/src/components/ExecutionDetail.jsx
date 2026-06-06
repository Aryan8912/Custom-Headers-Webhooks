import StatusBadge from "./StatusBadge";

const ExecutionDetail = ({ data, onClose }) => {
  if (!data) return null;

  return (
    <div style={{
      position: "fixed", inset: 0,
      background: "rgba(0,0,0,0.5)",
      display: "flex", alignItems: "center", justifyContent: "center",
      zIndex: 1000, padding: "24px",
    }}>
      <div style={{
        background: "white", borderRadius: "12px",
        width: "100%", maxWidth: "640px",
        maxHeight: "80vh", overflowY: "auto",
        boxShadow: "0 20px 60px rgba(0,0,0,0.2)",
      }}>
        {/* Header */}
        <div style={{
          padding: "20px 24px",
          borderBottom: "1px solid #e5e7eb",
          display: "flex", justifyContent: "space-between", alignItems: "center",
        }}>
          <h2 style={{ margin: 0, fontSize: "18px", fontWeight: "700" }}>
            Execution Detail
          </h2>
          <button onClick={onClose} style={{
            background: "none", border: "none",
            fontSize: "20px", cursor: "pointer", color: "#6b7280",
          }}>✕</button>
        </div>

        {/* Body */}
        <div style={{ padding: "24px" }}>

          {/* Status row */}
          <div style={{ display: "flex", gap: "12px", marginBottom: "24px", flexWrap: "wrap" }}>
            <StatusBadge status={data.status} />
            <span style={{
              padding: "2px 10px", borderRadius: "999px", fontSize: "12px",
              fontWeight: "600", background: data.auth_verified ? "#d1fae5" : "#fee2e2",
              color: data.auth_verified ? "#065f46" : "#991b1b",
            }}>
              {data.auth_verified ? "✓ Auth Verified" : "✗ Auth Failed"}
            </span>
            <span style={{
              padding: "2px 10px", borderRadius: "999px", fontSize: "12px",
              fontWeight: "600", background: data.forwarded ? "#d1fae5" : "#f3f4f6",
              color: data.forwarded ? "#065f46" : "#6b7280",
            }}>
              {data.forwarded ? "✓ Forwarded" : "— Not Forwarded"}
            </span>
          </div>

          {/* Fields */}
          {[
            { label: "Execution ID", value: data.execution_id },
            { label: "Agent ID", value: data.agent_id },
            { label: "Tenant ID", value: data.tenant_id },
            { label: "Forward Status", value: data.forward_status_code || "—" },
            { label: "Forward Error", value: data.forward_error || "—" },
            { label: "Created At", value: new Date(data.created_at).toLocaleString() },
            { label: "Updated At", value: new Date(data.updated_at).toLocaleString() },
          ].map(({ label, value }) => (
            <div key={label} style={{
              display: "flex", justifyContent: "space-between",
              padding: "10px 0", borderBottom: "1px solid #f3f4f6",
            }}>
              <span style={{ color: "#6b7280", fontSize: "13px", fontWeight: "500" }}>{label}</span>
              <span style={{ color: "#111827", fontSize: "13px", fontFamily: "monospace", maxWidth: "60%", wordBreak: "break-all", textAlign: "right" }}>
                {value}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default ExecutionDetail;