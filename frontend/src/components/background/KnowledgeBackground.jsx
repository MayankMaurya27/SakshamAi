import { useEffect, useRef } from "react";

export default function KnowledgeBackground({ intensity = "normal" }) {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return undefined;

    const ctx = canvas.getContext("2d");
    let width;
    let height;
    let animationFrame;
    const mouse = { x: null, y: null };
    const nodes = [];

    const nodeCount =
      intensity === "subtle"
        ? window.innerWidth > 1400
          ? 28
          : 18
        : window.innerWidth > 1400
          ? 52
          : 34;

    const resize = () => {
      width = canvas.width = window.innerWidth;
      height = canvas.height = window.innerHeight;
    };

    resize();

    const hues = ["amber", "cyan", "violet"];
    for (let i = 0; i < nodeCount; i++) {
      nodes.push({
        x: Math.random() * width,
        y: Math.random() * height,
        vx: (Math.random() - 0.5) * 0.12,
        vy: (Math.random() - 0.5) * 0.12,
        radius: Math.random() * 1.8 + 1.2,
        hue: hues[i % 3],
        pulse: Math.random() * Math.PI * 2,
      });
    }

    const handleMove = (e) => {
      mouse.x = e.clientX;
      mouse.y = e.clientY;
    };

    const handleLeave = () => {
      mouse.x = null;
      mouse.y = null;
    };

    window.addEventListener("resize", resize);
    window.addEventListener("mousemove", handleMove);
    window.addEventListener("mouseleave", handleLeave);

    const colorMap = {
      amber: { dot: "rgba(240, 180, 41, 0.55)", glow: "rgba(240, 180, 41, 0.06)", line: "rgba(240, 180, 41," },
      cyan: { dot: "rgba(34, 211, 238, 0.5)", glow: "rgba(34, 211, 238, 0.05)", line: "rgba(34, 211, 238," },
      violet: { dot: "rgba(192, 132, 252, 0.45)", glow: "rgba(192, 132, 252, 0.04)", line: "rgba(192, 132, 252," },
    };

    const draw = () => {
      ctx.clearRect(0, 0, width, height);

      for (const node of nodes) {
        node.x += node.vx;
        node.y += node.vy;
        node.pulse += 0.02;
        if (node.x < 0 || node.x > width) node.vx *= -1;
        if (node.y < 0 || node.y > height) node.vy *= -1;

        if (mouse.x && mouse.y) {
          const dx = node.x - mouse.x;
          const dy = node.y - mouse.y;
          const distance = Math.sqrt(dx * dx + dy * dy);
          if (distance < 180) {
            node.x += dx * 0.006;
            node.y += dy * 0.006;
          }
        }
      }

      for (let i = 0; i < nodes.length; i++) {
        for (let j = i + 1; j < nodes.length; j++) {
          const dx = nodes[i].x - nodes[j].x;
          const dy = nodes[i].y - nodes[j].y;
          const distance = Math.sqrt(dx * dx + dy * dy);

          if (distance < 180) {
            const alpha = 0.05 - distance / 5000;
            const c = colorMap[nodes[i].hue];
            ctx.beginPath();
            ctx.moveTo(nodes[i].x, nodes[i].y);
            ctx.lineTo(nodes[j].x, nodes[j].y);
            ctx.strokeStyle = `${c.line}${alpha})`;
            ctx.lineWidth = 0.6;
            ctx.stroke();
          }
        }
      }

      for (const node of nodes) {
        const c = colorMap[node.hue];
        const r = node.radius + Math.sin(node.pulse) * 0.4;

        ctx.beginPath();
        ctx.arc(node.x, node.y, r * 3.5, 0, Math.PI * 2);
        ctx.fillStyle = c.glow;
        ctx.fill();

        ctx.beginPath();
        ctx.arc(node.x, node.y, r, 0, Math.PI * 2);
        ctx.fillStyle = c.dot;
        ctx.fill();
      }

      animationFrame = requestAnimationFrame(draw);
    };

    draw();

    return () => {
      cancelAnimationFrame(animationFrame);
      window.removeEventListener("resize", resize);
      window.removeEventListener("mousemove", handleMove);
      window.removeEventListener("mouseleave", handleLeave);
    };
  }, [intensity]);

  return (
    <canvas
      ref={canvasRef}
      className="fixed inset-0 -z-10 pointer-events-none opacity-70"
      aria-hidden="true"
    />
  );
}
