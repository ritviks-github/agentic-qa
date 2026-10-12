import { Link } from "react-router-dom";
import Icon from "../components/Icon";
import StatusBadge from "../components/StatusBadge";
import { initialApplications } from "../data/loanData";

function Dashboard() {
  const total = initialApplications.length;

  const pending = initialApplications.filter(
    (item) =>
      item.status === "SUBMITTED" ||
      item.status === "UNDER_REVIEW" ||
      item.status === "DOCUMENT_VERIFICATION"
  ).length;

  const approved = initialApplications.filter(
    (item) => item.status === "APPROVED"
  ).length;

  const rejected = initialApplications.filter(
    (item) => item.status === "REJECTED"
  ).length;

  const stats = [
    {
      label: "Total Applications",
      value: total,
      type: "blue",
      icon: "file",
    },
    {
      label: "Pending Review",
      value: pending,
      type: "orange",
      icon: "clock",
    },
    {
      label: "Approved",
      value: approved,
      type: "green",
      icon: "checkCircle",
    },
    {
      label: "Rejected",
      value: rejected,
      type: "red",
      icon: "xCircle",
    },
  ];

  return (
    <>
      <div className="page-heading">
        <div>
          <h1>Dashboard</h1>
          <p>
            Overview of your loan application operations.
          </p>
        </div>

        <Link
          to="/applications/new"
          className="button primary"
        >
          <Icon name="plus" size={16} />
          New Application
        </Link>
      </div>

      <div className="stats-grid">
        {stats.map((stat) => (
          <div className="stat-card" key={stat.label}>
            <div className={`stat-icon ${stat.type}`}>
              <Icon name={stat.icon} size={19} />
            </div>

            <div>
              <span className="stat-label">{stat.label}</span>
              <strong className="stat-value">
                {stat.value}
              </strong>
            </div>
          </div>
        ))}
      </div>

      <section className="card">
        <div className="card-heading">
          <div>
            <h3>Recent Applications</h3>
            <p>Latest loan applications in the system.</p>
          </div>

          <Link to="/applications" className="text-link">
            View all
            <Icon name="arrowRight" size={14} />
          </Link>
        </div>

        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>Application ID</th>
                <th>Customer</th>
                <th>Loan Type</th>
                <th>Amount</th>
                <th>Status</th>
                <th></th>
              </tr>
            </thead>

            <tbody>
              {initialApplications.map((application) => (
                <tr key={application.id}>
                  <td>
                    <strong>{application.id}</strong>
                  </td>

                  <td>{application.name}</td>

                  <td>{application.loanType}</td>

                  <td>
                    ₹
                    {application.loanAmount.toLocaleString(
                      "en-IN"
                    )}
                  </td>

                  <td>
                    <StatusBadge
                      status={application.status}
                    />
                  </td>

                  <td>
                    <Link
                      className="table-link"
                      to={`/applications/${application.id}`}
                    >
                      View
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </>
  );
}

export default Dashboard;