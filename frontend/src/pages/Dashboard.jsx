import { useState } from "react";
import { useExecutions, useExecution } from "../hooks/useExecutions";
import ExecutionTable from "../components/ExecutionTable";
import ExecutionDetail from "../components/ExecutionDetail";

const Dashboard = () => {
  const [page, setPage] = useState(1);
  const [agentId, setAgentId] = useState("");
  const [status, setStatus] = useState("");
  const [selectedId, setSelectedId] = useState(null);

  const { data, isLoading, error, refetch } = useExecutions({
    page,
    pageSize: 20,
    agentId: agentId || undefined,
    status: status || undefined,
  });

  const { data: detail } = useExecution(selectedId);

  const totalPages = data ? Math.ceil(data.total / 20) : 1;

  return (
    <div style={{ minHeight: "100vh", background: "#f9fafb", fontFamily: "Inter, sans-serif" }}>

      {/* ── Header ── */}
      <div style={{
        background: "white", borderBottom: "1px solid #e5e7eb",
        padding: "16px 32px", display: "flex",
        justifyContent: "space-between", alignItems: "center",
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
          <div style={{
            width: "36px", height: "36px", background: "#6c63ff",
            borderRadius: "8px", display: "flex", alignItems: "center",
            justifyContent: "center", color: "white", fontWeight: "700",
          }}>B</div>
          <div>
            <h1 style={{ margin: 0, fontSize: "18px", fontWeight: "700" }}>
              Bolna Webhook Dashboard
            </h1>
            <p style={{ margin: 0, fontSize: "12px", color: "#6b7280" }}>
              Custom Headers · Execution Logs
            </p>
          </div>
        </div>
        <button
          onClick={() => refetch()}
          style={{
            background: "#6c63ff", color: "white", border: "none",
            padding: "8px 16px", borderRadius: "6px", cursor: "pointer",
            fontSize: "13px", fontWeight: "600",
          }}
        >
          ↻ Refresh
        </button>
      </div>

      <div style={{ padding: "32px", maxWidth: "1200px", margin: "0 auto" }}>

        {/* ── Stats ── */}
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: "16px", marginBottom: "24px" }}>
          {[
            { label: "Total Executions", value: data?.total ?? "—", color: "#6c63ff" },
            { label: "Current Page", value: page, color: "#059669" },
            { label: "Tenant", value: import.meta.env.VITE_TENANT_ID || "tenant_a", color: "#f59e0b" },
            { label: "Auto Refresh", value: "10s", color: "#3b82f6" },
          ].map(({ label, value, color }) => (
            <div key={label} style={{
              background: "white", border: "1px solid #e5e7eb",
              borderRadius: "8px", padding: "20px",
              borderTop: `3px solid ${color}`,
            }}>
              <p style={{ margin: "0 0 4px", fontSize: "12px", color: "#6b7280", fontWeight: "500" }}>{label}</p>
              <p style={{ margin: 0, fontSize: "24px", fontWeight: "700", color: "#111827" }}>{value}</p>
            </div>
          ))}
        </div>

        {/* ── Filters ── */}
        <div style={{
          background: "white", border: "1px solid #e5e7eb",
          borderRadius: "8px", padding: "16px 20px",
          marginBottom: "16px", display: "flex", gap: "12px", flexWrap: "wrap",
        }}>
          <input
            placeholder="Filter by Agent ID"
            value={agentId}
            onChange={e => { setAgentId(e.target.value); setPage(1); }}
            style={{
              border: "1px solid #d1d5db", borderRadius: "6px",
              padding: "8px 12px", fontSize: "13px", flex: 1, minWidth: "180px",
            }}
          />
          <select
            value={status}
            onChange={e => { setStatus(e.target.value); setPage(1); }}
            style={{
              border: "1px solid #d1d5db", borderRadius: "6px",
              padding: "8px 12px", fontSize: "13px", minWidth: "160px",
            }}
          >
            <option value="">All Statuses</option>
            <option value="completed">Completed</option>
            <option value="failed">Failed</option>
            <option value="in_progress">In Progress</option>
            <option value="queued">Queued</option>
            <option value="scheduled">Scheduled</option>
          </select>
          <button
            onClick={() => { setAgentId(""); setStatus(""); setPage(1); }}
            style={{
              border: "1px solid #d1d5db", background: "white",
              borderRadius: "6px", padding: "8px 16px",
              fontSize: "13px", cursor: "pointer", color: "#374151",
            }}
          >
            Clear
          </button>
        </div>

        {/* ── Error ── */}
        {error && (
          <div style={{
            background: "#fee2e2", border: "1px solid #fca5a5",
            borderRadius: "8px", padding: "12px 16px",
            color: "#991b1b", marginBottom: "16px", fontSize: "13px",
          }}>
            ⚠ Error loading executions: {error.message}
          </div>
        )}

        {/* ── Table ── */}
        <div style={{
          background: "white", border: "1px solid #e5e7eb",
          borderRadius: "8px", overflow: "hidden",
        }}>
          <div style={{
            padding: "16px 20px", borderBottom: "1px solid #e5e7eb",
            display: "flex", justifyContent: "space-between", alignItems: "center",
          }}>
            <h2 style={{ margin: 0, fontSize: "15px", fontWeight: "600" }}>
              Execution Logs
            </h2>
            <span style={{ fontSize: "12px", color: "#6b7280" }}>
              {data?.total ?? 0} total
            </span>
          </div>

          <ExecutionTable
            data={data}
            isLoading={isLoading}
            onSelect={setSelectedId}
          />

          {/* ── Pagination ── */}
          {data?.total > 0 && (
            <div style={{
              padding: "12px 20px", borderTop: "1px solid #e5e7eb",
              display: "flex", justifyContent: "space-between", alignItems: "center",
            }}>
              <span style={{ fontSize: "13px", color: "#6b7280" }}>
                Page {page} of {totalPages}
              </span>
              <div style={{ display: "flex", gap: "8px" }}>
                <button
                  onClick={() => setPage(p => Math.max(1, p - 1))}
                  disabled={page === 1}
                  style={{
                    border: "1px solid #d1d5db", background: "white",
                    borderRadius: "6px", padding: "6px 14px",
                    fontSize: "13px", cursor: page === 1 ? "not-allowed" : "pointer",
                    color: page === 1 ? "#9ca3af" : "#374151",
                  }}
                >← Prev</button>
                <button
                  onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                  disabled={page === totalPages}
                  style={{
                    border: "1px solid #d1d5db", background: "white",
                    borderRadius: "6px", padding: "6px 14px",
                    fontSize: "13px", cursor: page === totalPages ? "not-allowed" : "pointer",
                    color: page === totalPages ? "#9ca3af" : "#374151",
                  }}
                >Next →</button>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* ── Detail Modal ── */}
      {selectedId && detail && (
        <ExecutionDetail
          data={detail}
          onClose={() => setSelectedId(null)}
        />
      )}
    </div>
  );
};

export default Dashboard;