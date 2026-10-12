import { Outlet } from "react-router-dom";
import Sidebar from "./Sidebar";
import Topbar from "./Topbar";

function AppLayout() {
  return (
    <div className="app">
      <Sidebar />

      <div className="main">
        <Topbar />

        <main className="page">
          <Outlet />
        </main>
      </div>
    </div>
  );
}

export default AppLayout;