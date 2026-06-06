const STATUS_STYLES = {
  completed: "background:#d1fae5; color:#065f46; border:1px solid #6ee7b7",
  failed: "background:#fee2e2; color:#991b1b; border:1px solid #fca5a5",
  in_progress: "background:#dbeafe; color:#1e40af; border:1px solid #93c5fd",
  queued: "background:#fef9c3; color:#854d0e; border:1px solid #fde047",
  scheduled: "background:#f3e8ff; color:#6b21a8; border:1px solid #d8b4fe",
};

const StatusBadge = ({ status }) => {
  const style = STATUS_STYLES[status] || "background:#f3f4f6; color:#374151; border:1px solid #d1d5db";

  return (
    <span
      style={{
        ...Object.fromEntries(style.split(";").filter(Boolean).map(s => s.split(":"))),
        padding: "2px 10px",
        borderRadius: "999px",
        fontSize: "12px",
        fontWeight: "600",
        textTransform: "capitalize",
        whiteSpace: "nowrap",
      }}
    >
      {status}
    </span>
  );
};

export default StatusBadge;