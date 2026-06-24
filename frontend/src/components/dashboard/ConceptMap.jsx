import { useEffect, useRef } from "react";

export default function ConceptMap({ chapters, subject, classLevel }) {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas || chapters.length === 0) return undefined;

    const ctx = canvas.getContext("2d");
    const dpr = window.devicePixelRatio || 1;

    const resize = () => {
      const rect = canvas.getBoundingClientRect();

      canvas.width = rect.width * dpr;
      canvas.height = rect.height * dpr;

      ctx.setTransform(1, 0, 0, 1, 0, 0);
      ctx.scale(dpr, dpr);

      draw(rect.width, rect.height);
    };

    const draw = (width, height) => {
      ctx.clearRect(0, 0, width, height);

      const centerX = width / 2;
      const centerY = height / 2;

      const radius = Math.min(width, height) * 0.44;

      const nodes = chapters.map((ch, i) => {
        const angle =
          (i / chapters.length) * Math.PI * 2 - Math.PI / 2;

        return {
          x: centerX + Math.cos(angle) * radius,
          y: centerY + Math.sin(angle) * radius,
          label: ch.chapter_title,
          id: ch.chapter_id,
        };
      });

      // Background Glow
      ctx.beginPath();
      ctx.arc(centerX, centerY, radius + 90, 0, Math.PI * 2);

      const bgGlow = ctx.createRadialGradient(
        centerX,
        centerY,
        0,
        centerX,
        centerY,
        radius + 90
      );

      bgGlow.addColorStop(0, "rgba(34,211,238,0.10)");
      bgGlow.addColorStop(0.5, "rgba(192,132,252,0.05)");
      bgGlow.addColorStop(1, "rgba(0,0,0,0)");

      ctx.fillStyle = bgGlow;
      ctx.fill();

      // Connections
      nodes.forEach((node) => {
        ctx.beginPath();
        ctx.moveTo(centerX, centerY);
        ctx.lineTo(node.x, node.y);

        ctx.strokeStyle = "rgba(34,211,238,0.65)";
        ctx.lineWidth = 3;

        ctx.stroke();
      });

      // Center Node
      ctx.beginPath();

      ctx.shadowBlur = 50;
      ctx.shadowColor = "rgba(34,211,238,0.85)";

      ctx.arc(centerX, centerY, 60, 0, Math.PI * 2);

      const grad = ctx.createRadialGradient(
        centerX,
        centerY,
        0,
        centerX,
        centerY,
        60
      );

      grad.addColorStop(0, "#f59e0b");
      grad.addColorStop(0.6, "#d97706");
      grad.addColorStop(1, "#22d3ee");

      ctx.fillStyle = grad;
      ctx.fill();

      ctx.shadowBlur = 0;

      // Center Text
      ctx.fillStyle = "#04060f";
      ctx.font = "bold 16px Sora, sans-serif";
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";

      const centerLabel = `${subject || "Subject"}`.slice(0, 14);

      ctx.fillText(centerLabel, centerX, centerY - 10);

      ctx.font = "13px Sora, sans-serif";
      ctx.fillStyle = "rgba(4,6,15,0.85)";

      ctx.fillText(
        `Class ${classLevel || ""}`,
        centerX,
        centerY + 14
      );

      // Outer Nodes
      nodes.forEach((node, i) => {
        const primaryColor =
          i % 2 === 0
            ? "rgba(192,132,252,0.95)"
            : "rgba(34,211,238,0.95)";

        const outerColor =
          i % 2 === 0
            ? "rgba(192,132,252,0.12)"
            : "rgba(34,211,238,0.12)";

        // Glow Ring
        ctx.beginPath();

        ctx.shadowBlur = 30;
        ctx.shadowColor = primaryColor;

        ctx.arc(node.x, node.y, 36, 0, Math.PI * 2);

        ctx.fillStyle = outerColor;
        ctx.fill();

        // Main Node
        ctx.beginPath();

        ctx.arc(node.x, node.y, 16, 0, Math.PI * 2);

        ctx.fillStyle = primaryColor;
        ctx.fill();

        ctx.shadowBlur = 0;

        // Label
        ctx.fillStyle = "#e8edf7";
        ctx.font = "12px Sora, sans-serif";
        ctx.textAlign = "center";

        const label =
          node.label.length > 20
            ? `${node.label.slice(0, 18)}…`
            : node.label;

        const labelY =
          node.y > centerY
            ? node.y + 50
            : node.y - 38;

        ctx.fillText(label, node.x, labelY);
      });
    };

    resize();

    window.addEventListener("resize", resize);

    return () => {
      window.removeEventListener("resize", resize);
    };
  }, [chapters, subject, classLevel]);

  if (chapters.length === 0) {
    return (
      <div className="h-[500px] flex items-center justify-center text-ink-muted text-sm">
        Select a subject to view concept map
      </div>
    );
  }

  return (
    <div className="relative overflow-hidden rounded-3xl">
      <canvas
        ref={canvasRef}
        className="w-full h-[500px] lg:h-[650px]"
        aria-label={`Concept map for ${subject} class ${classLevel}`}
      />
    </div>
  );
}