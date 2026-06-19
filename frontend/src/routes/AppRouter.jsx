import { BrowserRouter, Routes, Route } from "react-router-dom";

import Home from "../pages/Home/Home";
import Learn from "../pages/Learn/Learn";
import Quiz from "../pages/Quiz/Quiz";
import Upload from "../pages/Upload/Upload";
import Dashboard from "../pages/Dashboard/Dashboard";
import Accessibility from "../pages/Accessibility/Accessibility";

export default function AppRouter() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/learn" element={<Learn />} />
        <Route path="/quiz" element={<Quiz />} />
        <Route path="/upload" element={<Upload />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/accessibility" element={<Accessibility />} />
      </Routes>
    </BrowserRouter>
  );
}