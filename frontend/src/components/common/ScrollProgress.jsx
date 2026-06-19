import { motion, useScroll } from "framer-motion";

export default function ScrollProgress() {
  const { scrollYProgress } = useScroll();

  return (
    <motion.div
      style={{
        scaleX: scrollYProgress,
      }}
      className="
        fixed
        top-0
        left-0
        right-0
        h-[3px]
        bg-[#1E3A5F]
        origin-left
        z-[9999]
      "
    />
  );
}