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
      ctx.scale(dpr, dpr);
      draw(rect.width, rect.height);
    };

    const draw = (width, height) => {
      ctx.clearRect(0, 0, width, height);

      const centerX = width / 2;
      const centerY = height / 2;
      const radius = Math.min(width, height) * 0.32;

      const nodes = chapters.map((ch, i) => {
        const angle = (i / chapters.length) * Math.PI * 2 - Math.PI / 2;
        return {
          x: centerX + Math.cos(angle) * radius,
          y: centerY + Math.sin(angle) * radius,
          label: ch.chapter_title,
          id: ch.chapter_id,
        };
      });

      nodes.forEach((node) => {
        ctx.beginPath();
        ctx.moveTo(centerX, centerY);
        ctx.lineTo(node.x, node.y);
        ctx.strokeStyle = "rgba(34, 211, 238, 0.25)";
        ctx.lineWidth = 1.5;
        ctx.stroke();
      });

      ctx.beginPath();
      ctx.arc(centerX, centerY, 28, 0, Math.PI * 2);
      const grad = ctx.createRadialGradient(
        centerX,
        centerY,
        0,
        centerX,
        centerY,
        28,
      );
      grad.addColorStop(0, "#d97706");
      grad.addColorStop(1, "#22d3ee");
      ctx.fillStyle = grad;
      ctx.fill();

      ctx.fillStyle = "#04060f";
      ctx.font = "bold 11px Sora, sans-serif";
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";
      const centerLabel = `${subject || "Subject"}`.slice(0, 12);
      ctx.fillText(centerLabel, centerX, centerY - 6);
      ctx.font = "10px Sora, sans-serif";
      ctx.fillStyle = "rgba(4, 6, 15, 0.75)";
      ctx.fillText(`Class ${classLevel}`, centerX, centerY + 8);

      nodes.forEach((node, i) => {
        ctx.beginPath();
        ctx.arc(node.x, node.y, 8, 0, Math.PI * 2);
        ctx.fillStyle =
          i % 2 === 0 ? "rgba(192, 132, 252, 0.75)" : "rgba(34, 211, 238, 0.75)";
        ctx.fill();

        ctx.beginPath();
        ctx.arc(node.x, node.y, 16, 0, Math.PI * 2);
        ctx.fillStyle =
          i % 2 === 0 ? "rgba(192, 132, 252, 0.1)" : "rgba(34, 211, 238, 0.1)";
        ctx.fill();

        ctx.fillStyle = "#e8edf7";
        ctx.font = "10px Sora, sans-serif";
        ctx.textAlign = "center";
        const label =
          node.label.length > 18
            ? `${node.label.slice(0, 16)}…`
            : node.label;
        const labelY = node.y + (node.y > centerY ? 28 : -20);
        ctx.fillText(label, node.x, labelY);
      });
    };

    resize();
    window.addEventListener("resize", resize);
    return () => window.removeEventListener("resize", resize);
  }, [chapters, subject, classLevel]);

  if (chapters.length === 0) {
    return (
      <div className="h-64 flex items-center justify-center text-ink-muted text-sm">
        Select a subject to view concept map
      </div>
    );
  }

  return (
    <canvas
      ref={canvasRef}
      className="w-full h-64 md:h-80"
      aria-label={`Concept map for ${subject} class ${classLevel}`}
    />
  );
}
