import { useEffect, useState } from "react";
import { Link, NavLink } from "react-router-dom";
import { Menu, X, ArrowRight } from "lucide-react";

import logo from "../../assets/logo/saksham-logo.png";

export default function Navbar() {
  const [mobileOpen, setMobileOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 20);
    };

    window.addEventListener("scroll", handleScroll);

    return () =>
      window.removeEventListener("scroll", handleScroll);
  }, []);

  const navLink = ({ isActive }) =>
    `
      relative
      font-medium
      transition-all
      duration-300
      ${
        isActive
          ? "text-[#1E3A5F]"
          : "text-slate-600 hover:text-[#1E3A5F]"
      }
    `;

  return (
    <nav
      className={`
        sticky
        top-0
        z-50
        transition-all
        duration-500
        ${
          scrolled
            ? "bg-white/75 backdrop-blur-xl border-b border-white/20 shadow-[0_10px_40px_rgba(15,23,42,0.06)]"
            : "bg-transparent"
        }
      `}
    >
      <div className="max-w-7xl mx-auto px-4 md:px-6">
        <div className="h-20 flex items-center justify-between">

          {/* Logo */}

          <Link
            to="/"
            className="
              flex
              items-center
              gap-3
              group
            "
          >
            <img
              src={logo}
              alt="Saksham AI"
              className="
                h-10
                w-10
                object-contain
                transition-transform
                duration-300
                group-hover:scale-110
              "
            />

            <div>
              <div className="font-bold text-xl text-[#1E3A5F]">
                Saksham AI
              </div>

              <div className="text-[11px] text-slate-500">
                Learning Without Barriers
              </div>
            </div>
          </Link>

          {/* Desktop Navigation */}

          <div className="hidden lg:flex items-center gap-8">

            <NavLink
              to="/learn"
              className={navLink}
            >
              Learn
            </NavLink>

            <NavLink
              to="/quiz"
              className={navLink}
            >
              Quiz
            </NavLink>

            <NavLink
              to="/upload"
              className={navLink}
            >
              Notes
            </NavLink>

            <NavLink
              to="/accessibility"
              className={navLink}
            >
              Accessibility
            </NavLink>

            <NavLink
              to="/dashboard"
              className={navLink}
            >
              Dashboard
            </NavLink>

            <Link
              to="/learn"
              className="
                flex
                items-center
                gap-2
                px-5
                py-2.5
                rounded-xl
                bg-[#1E3A5F]
                text-white
                font-semibold
                hover:translate-y-[-2px]
                transition-all
                shadow-lg
              "
            >
              Ask AI
              <ArrowRight size={16} />
            </Link>

          </div>

          {/* Mobile Menu Button */}

          <button
            onClick={() =>
              setMobileOpen(!mobileOpen)
            }
            className="
              lg:hidden
              text-[#1E3A5F]
            "
          >
            {mobileOpen ? (
              <X size={28} />
            ) : (
              <Menu size={28} />
            )}
          </button>

        </div>
      </div>

      {/* Mobile Menu */}

      {mobileOpen && (
        <div
          className="
            lg:hidden
            bg-white/95
            backdrop-blur-xl
            border-t
            border-slate-200
          "
        >
          <div className="px-5 py-5 space-y-4">

            <NavLink
              to="/learn"
              onClick={() =>
                setMobileOpen(false)
              }
              className="block py-2 text-slate-700 font-medium"
            >
              Learn
            </NavLink>

            <NavLink
              to="/quiz"
              onClick={() =>
                setMobileOpen(false)
              }
              className="block py-2 text-slate-700 font-medium"
            >
              Quiz
            </NavLink>

            <NavLink
              to="/upload"
              onClick={() =>
                setMobileOpen(false)
              }
              className="block py-2 text-slate-700 font-medium"
            >
              Notes
            </NavLink>

            <NavLink
              to="/accessibility"
              onClick={() =>
                setMobileOpen(false)
              }
              className="block py-2 text-slate-700 font-medium"
            >
              Accessibility
            </NavLink>

            <NavLink
              to="/dashboard"
              onClick={() =>
                setMobileOpen(false)
              }
              className="block py-2 text-slate-700 font-medium"
            >
              Dashboard
            </NavLink>

            <Link
              to="/learn"
              onClick={() =>
                setMobileOpen(false)
              }
              className="
                flex
                justify-center
                items-center
                gap-2
                bg-[#1E3A5F]
                text-white
                py-3
                rounded-xl
                font-semibold
              "
            >
              Ask AI
              <ArrowRight size={16} />
            </Link>

          </div>
        </div>
      )}
    </nav>
  );
}