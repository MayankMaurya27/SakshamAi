import { useEffect, useState } from "react";
import { Link, NavLink } from "react-router-dom";
import { Menu, X, ArrowRight, BookMarked } from "lucide-react";
import Logo from "../brand/Logo";

const navItems = [
  { to: "/learn", label: "Learn" },
  { to: "/quiz", label: "Quiz" },
  { to: "/upload", label: "Notes" },
  { to: "/dashboard", label: "Dashboard" },
  { to: "/accessibility", label: "Accessibility" },
];

export default function Navbar() {
  const [mobileOpen, setMobileOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 16);
    window.addEventListener("scroll", handleScroll, { passive: true });
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  useEffect(() => {
    document.body.style.overflow = mobileOpen ? "hidden" : "";
    return () => {
      document.body.style.overflow = "";
    };
  }, [mobileOpen]);

  const closeMobile = () => setMobileOpen(false);

  const linkClass = ({ isActive }) =>
    `relative text-sm font-semibold transition-colors duration-200 ${
      isActive ? "text-primary" : "text-ink-muted hover:text-accent"
    }`;

  return (
    <nav
      className={`
        sticky top-0 z-50 transition-all duration-500
        ${scrolled ? "glass-panel-strong shadow-soft" : "bg-transparent"}
      `}
      role="navigation"
      aria-label="Main navigation"
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="h-[72px] flex items-center justify-between gap-4">
          <Link
            to="/"
            className="flex items-center gap-3 group shrink-0"
            aria-label="Saksham AI home"
            onClick={closeMobile}
          >
            <Logo
              size={42}
              className="transition-transform duration-300 group-hover:scale-105"
            />
            <div className="hidden sm:block">
              <div className="font-bold text-lg text-primary leading-tight">
                Saksham AI
              </div>
              <div className="text-[11px] text-ink-muted font-medium tracking-wide">
                Learning Without Barriers
              </div>
            </div>
          </Link>

          <div className="hidden lg:flex items-center gap-8">
            {navItems.map((item) => (
              <NavLink key={item.to} to={item.to} className={linkClass}>
                {({ isActive }) => (
                  <>
                    {item.label}
                    {isActive && (
                      <span className="absolute -bottom-1 left-0 right-0 h-0.5 bg-gradient-to-r from-primary to-accent rounded-full" />
                    )}
                  </>
                )}
              </NavLink>
            ))}
          </div>

          <div className="flex items-center gap-3">
            <Link
              to="/learn"
              className="
                hidden sm:inline-flex items-center gap-2
                px-5 py-2.5 rounded-xl
                bg-gradient-to-br from-primary to-primary-dark text-void text-sm font-semibold
                shadow-amber hover:brightness-110
                transition-all duration-200 hover:-translate-y-0.5
                focus-ring
              "
            >
              <BookMarked size={15} />
              Workspace
              <ArrowRight size={15} />
            </Link>

            <button
              type="button"
              onClick={() => setMobileOpen(!mobileOpen)}
              className="lg:hidden p-2 rounded-xl text-primary hover:bg-primary/10 focus-ring"
              aria-label={mobileOpen ? "Close menu" : "Open menu"}
              aria-expanded={mobileOpen}
            >
              {mobileOpen ? <X size={24} /> : <Menu size={24} />}
            </button>
          </div>
        </div>
      </div>

      {mobileOpen && (
        <div className="lg:hidden glass-panel-strong border-t border-border">
          <div className="px-5 py-5 space-y-1">
            {navItems.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                onClick={closeMobile}
                className={({ isActive }) =>
                  `block px-4 py-3 rounded-xl font-semibold transition-colors ${
                    isActive
                      ? "bg-primary/12 text-primary"
                      : "text-ink-muted hover:bg-accent/8 hover:text-accent"
                  }`
                }
              >
                {item.label}
              </NavLink>
            ))}
            <Link
              to="/learn"
              onClick={closeMobile}
              className="
                flex justify-center items-center gap-2 mt-3
                bg-gradient-to-br from-primary to-primary-dark text-void py-3.5 rounded-xl font-semibold
              "
            >
              <BookMarked size={16} />
              Open Workspace
            </Link>
          </div>
        </div>
      )}
    </nav>
  );
}
