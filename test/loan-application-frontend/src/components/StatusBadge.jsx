function StatusBadge({ status }) {
  const classes = {
    DRAFT: "draft",
    SUBMITTED: "submitted",
    UNDER_REVIEW: "review",
    DOCUMENT_VERIFICATION: "review",
    APPROVED: "approved",
    REJECTED: "rejected",
    CANCELLED: "rejected",
    DISBURSED: "approved",
  };

  const text = status
    ?.replaceAll("_", " ")
    .toLowerCase()
    .replace(/\b\w/g, (letter) => letter.toUpperCase());

  return (
    <span className={`status ${classes[status] || ""}`}>
      {text}
    </span>
  );
}

export default StatusBadge;