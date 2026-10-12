import { Link } from "react-router-dom";
import Icon from "../components/Icon";
import StatusBadge from "../components/StatusBadge";
import { initialApplications } from "../data/loanData";

function Applications() {
  return (
    <>
      <div className="page-heading">
        <div>
          <h1>Applications</h1>
          <p>View and manage all loan applications.</p>
        </div>

        <Link
          to="/applications/new"
          className="button primary"
        >
          <Icon name="plus" size={16} />
          New Application
        </Link>
      </div>

      <section className="card">
        <div className="filter-bar">
          <div className="search-input">
            <Icon name="search" size={16} />

            <input
              placeholder="Search applications..."
            />
          </div>

          <select>
            <option>All Statuses</option>
            <option>Draft</option>
            <option>Submitted</option>
            <option>Under Review</option>
            <option>Approved</option>
            <option>Rejected</option>
          </select>

          <button className="filter-button">
            <Icon name="filter" size={15} />
            Filter
          </button>
        </div>

        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>Application ID</th>
                <th>Customer</th>
                <th>Loan Type</th>
                <th>Amount</th>
                <th>Eligibility</th>
                <th>Status</th>
                <th>Created</th>
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
                    <span
                      className={
                        application.eligibility === "ELIGIBLE"
                          ? "success-text"
                          : "danger-text"
                      }
                    >
                      {application.eligibility.replaceAll(
                        "_",
                        " "
                      )}
                    </span>
                  </td>

                  <td>
                    <StatusBadge
                      status={application.status}
                    />
                  </td>

                  <td>{application.createdAt}</td>

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

export default Applications;