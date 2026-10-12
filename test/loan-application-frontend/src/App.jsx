import { Routes, Route } from "react-router-dom";

import AppLayout from "./components/AppLayout";

import Dashboard from "./pages/Dashboard";
import Applications from "./pages/Applications";
import NewApplication from "./pages/NewApplication";
import ApplicationDetails from "./pages/ApplicationDetails";
import Documents from "./pages/Documents";
import Eligibility from "./pages/Eligibility";
import ReviewApplications from "./pages/ReviewApplications";
import TrackApplication from "./pages/TrackApplication";
import AuditTrail from "./pages/AuditTrail";

function App() {
  return (
    <Routes>
      <Route path="/" element={<AppLayout />}>
        <Route index element={<Dashboard />} />

        <Route path="applications" element={<Applications />} />

        <Route
          path="applications/new"
          element={<NewApplication />}
        />

        <Route
          path="applications/:id"
          element={<ApplicationDetails />}
        />

        <Route
          path="applications/:id/documents"
          element={<Documents />}
        />

        <Route
          path="applications/:id/eligibility"
          element={<Eligibility />}
        />

        <Route
          path="review"
          element={<ReviewApplications />}
        />

        <Route
          path="track"
          element={<TrackApplication />}
        />

        <Route
          path="audit"
          element={<AuditTrail />}
        />
      </Route>
    </Routes>
  );
}

export default App;