import Navbar from "./Navbar";
import Footer from "./Footer";

export default function MainLayout({ children, fullWidth = false }) {
  return (
    <div className="min-h-screen flex flex-col">
      <Navbar />
      <main
        className={`flex-1 ${fullWidth ? "" : ""}`}
        id="main-content"
      >
        {children}
      </main>
      <Footer />
    </div>
  );
}
