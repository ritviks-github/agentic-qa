import Icon from "./Icon";

function Topbar() {
  return (
    <header className="topbar">
      <div>
        <h2>Loan Application Management</h2>
        <p>
          Manage applications, eligibility and approvals
        </p>
      </div>

      <div className="topbar-right">
        <button className="notification">
          <Icon name="bell" size={18} />
          <span></span>
        </button>

        <div className="topbar-user">
          <div className="avatar small">AD</div>

          <div>
            <strong>Admin User</strong>
            <span>Operations</span>
          </div>
        </div>
      </div>
    </header>
  );
}

export default Topbar;