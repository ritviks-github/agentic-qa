import { useState } from "react";
import Icon from "../components/Icon";
import StatusBadge from "../components/StatusBadge";
import { initialApplications } from "../data/loanData";

function TrackApplication() {
  const [id, setId] = useState("");
  const [application, setApplication] =
    useState(null);

  const search = () => {
    const result = initialApplications.find(
      (item) =>
        item.id.toLowerCase() === id.toLowerCase()
    );

    setApplication(result || null);
  };

  return (
    <>
      <div className="page-heading">
        <div>
          <h1>Track Application</h1>
          <p>
            Check the current status of a loan application.
          </p>
        </div>
      </div>

      <section className="card tracking-card">
        <div className="tracking-search">
          <label>Application ID</label>

          <div className="search-row">
            <input
              value={id}
              onChange={(e) => setId(e.target.value)}
              placeholder="e.g. LN-2026-1001"
            />

            <button
              className="button primary"
              onClick={search}
            >
              <Icon name="search" size={15} />
              Search
            </button>
          </div>
        </div>

        {application && (
          <div className="tracking-result">
            <div className="tracking-header">
              <div>
                <span>Application</span>
                <h3>{application.id}</h3>
              </div>

              <StatusBadge status={application.status} />
            </div>

            <div className="timeline">
              <div className="timeline-item completed">
                <div className="timeline-dot">
                  <Icon name="check" size={13} />
                </div>

                <div>
                  <strong>Application Created</strong>
                  <span>01 Oct 2026</span>
                </div>
              </div>

              <div className="timeline-item completed">
                <div className="timeline-dot">
                  <Icon name="check" size={13} />
                </div>

                <div>
                  <strong>Application Submitted</strong>
                  <span>01 Oct 2026</span>
                </div>
              </div>

              <div className="timeline-item completed">
                <div className="timeline-dot">
                  <Icon name="check" size={13} />
                </div>

                <div>
                  <strong>Under Review</strong>
                  <span>02 Oct 2026</span>
                </div>
              </div>

              <div className="timeline-item">
                <div className="timeline-dot">4</div>

                <div>
                  <strong>Final Decision</strong>
                  <span>Pending</span>
                </div>
              </div>
            </div>
          </div>
        )}

        {id && !application && (
          <div className="empty-state">
            <Icon name="search" size={30} />

            <h3>Application not found</h3>

            <p>
              Please check the application ID and try again.
            </p>
          </div>
        )}
      </section>
    </>
  );
}

export default TrackApplication;