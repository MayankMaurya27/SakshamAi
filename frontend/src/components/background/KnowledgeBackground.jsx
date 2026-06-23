import { useEffect, useRef } from "react";

export default function KnowledgeBackground() {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    const ctx = canvas.getContext("2d");

    let width;
    let height;
    let animationFrame;

    const mouse = {
      x: null,
      y: null,
    };

    const nodes = [];

    const resize = () => {
      width = canvas.width = window.innerWidth;
      height = canvas.height = window.innerHeight;
    };

    resize();

    const nodeCount = window.innerWidth > 1400 ? 40 : 28;

    for (let i = 0; i < nodeCount; i++) {
      nodes.push({
        x: Math.random() * width,
        y: Math.random() * height,
        baseX: 0,
        baseY: 0,
        vx: (Math.random() - 0.5) * 0.2,
        vy: (Math.random() - 0.5) * 0.2,
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

    const draw = () => {
      ctx.clearRect(0, 0, width, height);

      for (const node of nodes) {
        node.x += node.vx;
        node.y += node.vy;

        if (node.x < 0 || node.x > width) node.vx *= -1;
        if (node.y < 0 || node.y > height) node.vy *= -1;

        if (mouse.x && mouse.y) {
          const dx = node.x - mouse.x;
          const dy = node.y - mouse.y;

          const distance = Math.sqrt(dx * dx + dy * dy);

          if (distance < 140) {
            node.x += dx * 0.01;
            node.y += dy * 0.01;
          }
        }
      }

      for (let i = 0; i < nodes.length; i++) {
        for (let j = i + 1; j < nodes.length; j++) {
          const dx = nodes[i].x - nodes[j].x;
          const dy = nodes[i].y - nodes[j].y;

          const distance = Math.sqrt(dx * dx + dy * dy);

          if (distance < 220) {
            ctx.beginPath();
            ctx.moveTo(nodes[i].x, nodes[i].y);
            ctx.lineTo(nodes[j].x, nodes[j].y);

            ctx.strokeStyle = `rgba(30,58,95,${
              0.05 - distance / 4500
            })`;

            ctx.lineWidth = 1;
            ctx.stroke();
          }
        }
      }

      for (const node of nodes) {
        ctx.beginPath();
        ctx.arc(node.x, node.y, 3.8, 0, Math.PI * 2);

        ctx.fillStyle = "rgba(30,58,95,0.65)";
        ctx.fill();

        ctx.beginPath();
        ctx.arc(node.x, node.y, 8, 0, Math.PI * 2);

        ctx.fillStyle = "rgba(30,58,95,0.05)";
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
  }, []);

  return (
    <>
      <div
        className="
          fixed
          inset-0
          -z-20
          bg-gradient-to-br
          from-slate-100
          via-slate-50
          to-emerald-50
        "
      />

      <canvas
        ref={canvasRef}
        className="fixed inset-0 -z-10 opacity-70"
      />
    </>
  );
}