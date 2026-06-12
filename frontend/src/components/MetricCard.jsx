import React from "react";

export default function MetricCard({ title, value, hint, icon, alert }) {
  const renderIcon = () => {
    if (!icon) return null;
    if (typeof icon === "function") {
      const Icon = icon;
      return <Icon size={20} />;
    }
    return icon;
  };

  return (
    <section className={`metric-card${alert ? " alert" : ""}`}>
      <div className="metric-icon">{renderIcon()}</div>
      <div>
        <p>{title}</p>
        <strong>{value}</strong>
        {hint ? <span>{hint}</span> : null}
      </div>
    </section>
  );
}
