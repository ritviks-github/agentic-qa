import Icon from "../components/Icon";
import { auditEvents } from "../data/loanData";

function AuditTrail() {
  return (
    <>
      <div className="page-heading">
        <div>
          <h1>Audit Trail</h1>
          <p>
            Complete history of significant application
            activities.
          </p>
        </div>
      </div>

      <section className="card">
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>Event</th>
                <th>Application</th>
                <th>Actor</th>
                <th>Timestamp</th>
              </tr>
            </thead>

            <tbody>
              {auditEvents.map((event) => (
                <tr key={event.id}>
                  <td>
                    <div className="audit-event">
                      <div className="audit-icon">
                        <Icon name="shield" size={15} />
                      </div>

                      <strong>{event.event}</strong>
                    </div>
                  </td>

                  <td>{event.applicationId}</td>

                  <td>{event.actor}</td>

                  <td>{event.timestamp}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </>
  );
}

export default AuditTrail;