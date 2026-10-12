import { NavLink } from "react-router-dom";
import Icon from "./Icon";

function Sidebar() {
  const links = [
    {
      name: "Dashboard",
      path: "/",
      icon: "grid",
    },
    {
      name: "Applications",
      path: "/applications",
      icon: "file",
    },
    {
      name: "New Application",
      path: "/applications/new",
      icon: "plus",
    },
    {
      name: "Review Applications",
      path: "/review",
      icon: "check",
    },
    {
      name: "Track Application",
      path: "/track",
      icon: "search",
    },
    {
      name: "Audit Trail",
      path: "/audit",
      icon: "shield",
    },
  ];

  return (
    <aside className="sidebar">
      <div className="brand">
        <div className="brand-mark">
          <span>LF</span>
        </div>

        <div>
          <div className="brand-name">LoanFlow</div>
          <div className="brand-caption">
            Loan Management
          </div>
        </div>
      </div>

      <div className="nav-label">MAIN MENU</div>

      <nav className="sidebar-nav">
        {links.map((link) => (
          <NavLink
            key={link.path}
            to={link.path}
            end={link.path === "/"}
            className={({ isActive }) =>
              `nav-item ${isActive ? "active" : ""}`
            }
          >
            <Icon name={link.icon} size={17} />
            <span>{link.name}</span>
          </NavLink>
        ))}
      </nav>

      <div className="sidebar-bottom">
        <div className="avatar">AD</div>

        <div className="sidebar-user">
          <strong>Admin User</strong>
          <span>Operations</span>
        </div>
      </div>
    </aside>
  );
}

export default Sidebar;