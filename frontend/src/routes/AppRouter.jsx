import { lazy, Suspense } from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { Navigate } from "react-router-dom";
import { LoadingState } from "../components/ui/Spinner";

const Summary = lazy(() => import("../pages/Summary/Summary"));
const Home = lazy(() => import("../pages/Home/Home"));
const Learn = lazy(() => import("../pages/Learn/Learn"));
const Quiz = lazy(() => import("../pages/Quiz/Quiz"));
const Upload = lazy(() => import("../pages/Upload/Upload"));
const Dashboard = lazy(() => import("../pages/Dashboard/Dashboard"));
const Accessibility = lazy(() => import("../pages/Accessibility/Accessibility"));

function PageLoader() {
  return (
    <div className="min-h-[60vh] flex items-center justify-center">
      <LoadingState message="Loading workspace..." />
    </div>
  );
}

export default function AppRouter() {
  return (
    <BrowserRouter>
      <Suspense fallback={<PageLoader />}>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/learn" element={<Learn />} />
          <Route path="/summary" element={<Summary />} />
          <Route path="/quiz" element={<Quiz />} />
          <Route path="/upload" element={<Upload />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/accessibility" element={<Accessibility />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Suspense>
    </BrowserRouter>
  );
}
